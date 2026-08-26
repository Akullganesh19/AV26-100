import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union
from sqlalchemy import text, bindparam

from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from uuid import UUID

FEATURE_NAMES = [
    "confirmed_cases_lag1",
    "confirmed_cases_lag2",
    "confirmed_cases_lag3",
    "confirmed_cases_lag4",
    "cases_rolling_mean_4wk",
    "cases_rolling_std_4wk",
    "temperature_c",
    "humidity_pct",
    "vaccination_coverage_pct",
]

# Note: cases_rolling_std_4wk is imputed with 0.0 as zero variance 
# is a defensible baseline for short histories.
FEATURE_NOTES = {
    "imputation": {
        "cases_rolling_std_4wk": 0.0,
        "others": "mean"
    }
}

class FeatureBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build(
        self, 
        district_id: Union[str, UUID], 
        disease: str,
        as_of_date: Optional[Any] = None # Use Any for date for now, will refine later
    ) -> pd.DataFrame:
        """
        Builds the feature matrix using SQL Window Functions for high-performance lag/rolling calculations.
        """
        query = text("""
            WITH lagged_cases AS (
                SELECT
                    district_id,
                    disease,
                    week_start_date,
                    confirmed_cases,
                    LAG(confirmed_cases, 1) OVER w AS confirmed_cases_lag1,
                    LAG(confirmed_cases, 2) OVER w AS confirmed_cases_lag2,
                    LAG(confirmed_cases, 3) OVER w AS confirmed_cases_lag3,
                    LAG(confirmed_cases, 4) OVER w AS confirmed_cases_lag4,
                    AVG(confirmed_cases) OVER (w ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS cases_rolling_mean_4wk,
                    STDDEV(confirmed_cases) OVER (w ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS cases_rolling_std_4wk
                FROM raw_data
                WINDOW w AS (PARTITION BY district_id, disease ORDER BY week_start_date)
            ),
            latest_env AS (
                SELECT 
                    district_id, 
                    date,
                    temperature_c,
                    humidity_pct
                FROM environmental_data
            ),
            latest_vacc AS (
                SELECT 
                    district_id, 
                    disease, 
                    coverage_pct AS vaccination_coverage_pct
                FROM vaccination_coverage
            )
            SELECT 
                lc.*,
                e.temperature_c,
                e.humidity_pct,
                v.vaccination_coverage_pct
            FROM lagged_cases lc
            LEFT JOIN latest_env e ON lc.district_id = e.district_id AND lc.week_start_date = e.date
            LEFT JOIN latest_vacc v ON lc.district_id = v.district_id AND lc.disease = v.disease
            WHERE lc.district_id = :d_id AND lc.disease = :disease
            ORDER BY lc.week_start_date DESC
        """)
        
        params = {"d_id": str(district_id), "disease": disease}
        
        result = await self.db.execute(query, params)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        # Post-processing: Ensure types and handle the rolling std imputation
        if not df.empty:
            df["cases_rolling_std_4wk"] = df["cases_rolling_std_4wk"].fillna(0.0)
        
        # Take the most recent row up to as_of_date if provided
        if as_of_date:
            df = df[df["week_start_date"] <= as_of_date]
        
        if not df.empty:
            return pd.DataFrame([df.sort_values("week_start_date", ascending=False).iloc[0]])
        return pd.DataFrame()

    async def build_batch(
        self,
        district_ids: List[Union[str, UUID]],
        disease: str,
        as_of_date: Optional[Any] = None
    ) -> pd.DataFrame:
        """
        Builds the feature matrix for multiple districts in a single query.
        Returns a DataFrame containing one row per district (the most recent record).
        """
        if not district_ids:
            return pd.DataFrame()

        # Format IDs for IN clause
        id_strings = [str(d) for d in district_ids]
        # SQL parameter binding for an IN clause with SQLAlchemy requires a tuple

        query = text("""
            WITH lagged_cases AS (
                SELECT
                    district_id,
                    disease,
                    week_start_date,
                    confirmed_cases,
                    LAG(confirmed_cases, 1) OVER w AS confirmed_cases_lag1,
                    LAG(confirmed_cases, 2) OVER w AS confirmed_cases_lag2,
                    LAG(confirmed_cases, 3) OVER w AS confirmed_cases_lag3,
                    LAG(confirmed_cases, 4) OVER w AS confirmed_cases_lag4,
                    AVG(confirmed_cases) OVER (w ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS cases_rolling_mean_4wk,
                    STDDEV(confirmed_cases) OVER (w ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS cases_rolling_std_4wk
                FROM raw_data
                WHERE district_id IN :d_ids AND disease = :disease
                WINDOW w AS (PARTITION BY district_id, disease ORDER BY week_start_date)
            ),
            latest_env AS (
                SELECT
                    district_id,
                    date,
                    temperature_c,
                    humidity_pct
                FROM environmental_data
                WHERE district_id IN :d_ids
            ),
            latest_vacc AS (
                SELECT
                    district_id,
                    disease,
                    coverage_pct AS vaccination_coverage_pct
                FROM vaccination_coverage
                WHERE district_id IN :d_ids AND disease = :disease
            )
            SELECT
                lc.*,
                e.temperature_c,
                e.humidity_pct,
                v.vaccination_coverage_pct
            FROM lagged_cases lc
            LEFT JOIN latest_env e ON lc.district_id = e.district_id AND lc.week_start_date = e.date
            LEFT JOIN latest_vacc v ON lc.district_id = v.district_id AND lc.disease = v.disease
            WHERE lc.week_start_date <= :as_of_date
            ORDER BY lc.district_id, lc.week_start_date DESC
        """).bindparams(bindparam("d_ids", expanding=True))

        # Need to cast list to tuple for IN clause binding in SQLAlchemy text()
        params = {"d_ids": tuple(id_strings), "disease": disease, "as_of_date": as_of_date if as_of_date else '9999-12-31'}

        result = await self.db.execute(query, params)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Post-processing: Ensure types and handle the rolling std imputation
        if not df.empty:
            df["cases_rolling_std_4wk"] = df["cases_rolling_std_4wk"].fillna(0.0)

        # Take the most recent row up to as_of_date if provided
        if as_of_date:
            df = df[df["week_start_date"] <= as_of_date]

        if not df.empty:
            # Sort and pick the most recent for each district
            df = df.sort_values(["district_id", "week_start_date"], ascending=[True, False])
            df = df.drop_duplicates(subset=["district_id"], keep="first").reset_index(drop=True)
            return df
        return pd.DataFrame()


def get_preprocessing_pipeline() -> Pipeline:
    """
    Returns a standardized preprocessing pipeline to prevent train/serve skew.
    """
    # Keyset: Districts with < 4 weeks of history will yield NaNs.
    # We use constant 0 imputation for lags to ensure the scaler receives a valid vector.
    
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ("scaler", StandardScaler()) # StandardScaler handles NaNs if imputer doesn't fill all
    ])

    preprocessor = ColumnTransformer(
        transformers=[ # Ensure all FEATURE_NAMES are passed to the preprocessor
            ("num", numeric_transformer, FEATURE_NAMES)
        ]
    )

    return Pipeline(steps=[("preprocessor", preprocessor)])
