import os
import asyncio
import joblib
import json
import pandas as pd
import numpy as np
import shap
from datetime import datetime, UTC
from pathlib import Path
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, f1_score
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import SessionLocal
from app.ml.features import FeatureBuilder, get_preprocessing_pipeline, FEATURE_NAMES
from app.models.model_metric import ModelMetric


MODELS_DIR = Path("models")
os.makedirs(MODELS_DIR, exist_ok=True)


def _synthetic_risk_score(row: pd.Series) -> float:
    """
    Deterministic synthetic risk label for training.
    Combines epidemiological signal with environmental factors.
    """
    case_growth = max(0, (row.get("confirmed_cases_lag1", 0) or 0) - (row.get("confirmed_cases_lag2", 0) or 0))
    rainfall_factor = (row.get("rainfall_mm", 0) or 0) * 0.3
    humidity_factor = max(0, (row.get("humidity_pct", 60) or 60) - 50) * 0.5
    vacc_penalty = max(0, 80 - (row.get("vaccination_coverage_pct", 60) or 60)) * 0.4
    base = case_growth * 1.5 + rainfall_factor + humidity_factor + vacc_penalty
    noise = np.random.uniform(-5, 5)
    return float(np.clip(base + noise + 10, 0, 100))


def _get_tier(score: float) -> int:
    """Map continuous risk score to 4-class tier label."""
    if score >= 75:
        return 3  # critical
    if score >= 50:
        return 2  # high
    if score >= 25:
        return 1  # medium
    return 0      # low


async def load_training_data(db: AsyncSession) -> pd.DataFrame:
    """
    Load all raw_data with environmental and vaccination data joined.
    Returns a flat DataFrame ready for feature engineering.
    """
    query = text("""
        SELECT
            r.district_id,
            r.disease,
            r.week_start_date,
            r.confirmed_cases,
            LAG(r.confirmed_cases, 1) OVER w AS confirmed_cases_lag1,
            LAG(r.confirmed_cases, 2) OVER w AS confirmed_cases_lag2,
            LAG(r.confirmed_cases, 3) OVER w AS confirmed_cases_lag3,
            LAG(r.confirmed_cases, 4) OVER w AS confirmed_cases_lag4,
            AVG(r.confirmed_cases) OVER (w ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS cases_rolling_mean_4wk,
            STDDEV(r.confirmed_cases) OVER (w ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS cases_rolling_std_4wk,
            COALESCE(e.temperature_c, 28.0) AS temperature_c,
            COALESCE(e.humidity_pct, 65.0) AS humidity_pct,
            COALESCE(e.rainfall_mm, 5.0) AS rainfall_mm,
            COALESCE(v.coverage_pct, 60.0) AS vaccination_coverage_pct
        FROM raw_data r
        LEFT JOIN environmental_data e
            ON r.district_id = e.district_id AND r.week_start_date = e.date
        LEFT JOIN vaccination_coverage v
            ON r.district_id = v.district_id AND r.disease = v.disease
        WINDOW w AS (PARTITION BY r.district_id, r.disease ORDER BY r.week_start_date)
        ORDER BY r.week_start_date
    """)
    result = await db.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


async def train_model():
    print("=" * 60)
    print("Starting EpiSense model training pipeline...")
    print("=" * 60)

    async with SessionLocal() as db:
        # 1. Load Data
        df = await load_training_data(db)

        if df.empty or len(df) < 50:
            print(f"ERROR: Not enough data to train. Got {len(df)} rows, need >= 50.")
            print("Run: python scripts/seed.py first.")
            return

        print(f"Loaded {len(df)} rows across {df['district_id'].nunique()} districts.")

        # 2. Fill NaN lags with 0 (valid for start of history)
        df["cases_rolling_std_4wk"] = df["cases_rolling_std_4wk"].fillna(0.0)
        for col in FEATURE_NAMES:
            if col in df.columns:
                df[col] = df[col].fillna(0.0)

        # 3. Synthetic risk score label
        np.random.seed(42)
        df["risk_score"] = df.apply(_synthetic_risk_score, axis=1)
        df["risk_tier"] = df["risk_score"].apply(_get_tier)

        # 4. Temporal Split (80/20 by week)
        df = df.sort_values("week_start_date")
        sorted_weeks = df["week_start_date"].unique()
        cutoff_idx = int(len(sorted_weeks) * 0.80)
        cutoff_date = sorted_weeks[cutoff_idx]

        train_df = df[df["week_start_date"] <= cutoff_date].copy()
        val_df = df[df["week_start_date"] > cutoff_date].copy()

        print(f"Train: {len(train_df)} rows | Val: {len(val_df)} rows | Cutoff: {cutoff_date}")

        X_train_raw = train_df[FEATURE_NAMES]
        y_train_reg = train_df["risk_score"].values
        y_train_clf = train_df["risk_tier"].values

        X_val_raw = val_df[FEATURE_NAMES]
        y_val_reg = val_df["risk_score"].values
        y_val_clf = val_df["risk_tier"].values

        # 5. Preprocessing Pipeline
        pipeline = get_preprocessing_pipeline()
        X_train = pipeline.fit_transform(X_train_raw)
        X_val = pipeline.transform(X_val_raw)

        # 6. Train Regressor
        print("\nTraining XGBoost Regressor (risk score 0-100)...")
        regressor = XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
        )
        regressor.fit(X_train, y_train_reg, eval_set=[(X_val, y_val_reg)], verbose=False)

        # 7. Stacked Classifier (regressor score as extra feature)
        print("Training XGBoost Classifier (risk tier 0-3, stacked)...")
        train_scores = regressor.predict(X_train)
        val_scores = regressor.predict(X_val)

        X_train_stacked = np.column_stack((X_train, train_scores))
        X_val_stacked = np.column_stack((X_val, val_scores))

        classifier = XGBClassifier(
            n_estimators=200,
            max_depth=5,
            objective="multi:softmax",
            num_class=4,
            random_state=42,
            n_jobs=-1,
        )
        classifier.fit(X_train_stacked, y_train_clf, eval_set=[(X_val_stacked, y_val_clf)], verbose=False)

        # 8. Evaluation
        mae = float(mean_absolute_error(y_val_reg, val_scores))
        rmse = float(root_mean_squared_error(y_val_reg, val_scores))
        val_clf_preds = classifier.predict(X_val_stacked)
        f1 = float(f1_score(y_val_clf, val_clf_preds, average="weighted"))

        print(f"\n📊 Metrics: MAE={mae:.2f} | RMSE={rmse:.2f} | F1={f1:.4f}")

        # 9. SHAP Explainer
        print("Generating SHAP TreeExplainer...")
        sample_size = min(100, len(X_train))
        explainer = shap.TreeExplainer(regressor, data=shap.sample(X_train, sample_size))

        # 10. Feature bounds (p01 / p99) for OOD detection
        feature_bounds = {}
        for feat in FEATURE_NAMES:
            if feat in X_train_raw.columns:
                feature_bounds[feat] = {
                    "p01": float(np.percentile(X_train_raw[feat].dropna(), 1)),
                    "p99": float(np.percentile(X_train_raw[feat].dropna(), 99)),
                }

        # 11. Deployment gate (compare MAE with previous model)
        should_deploy = True
        try:
            with open(MODELS_DIR / "latest.json", "r") as f:
                current_manifest = json.load(f)
                prev_mae = current_manifest.get("metrics", {}).get("mae", float("inf"))
                if mae >= prev_mae * 1.05:
                    print(f"⚠️  Safety Gate: New MAE ({mae:.2f}) worse than previous ({prev_mae:.2f}). Aborting.")
                    should_deploy = False
                else:
                    print(f"✅ Safety Gate: Passed. New MAE ({mae:.2f}) vs Previous ({prev_mae:.2f}).")
        except FileNotFoundError:
            print("ℹ️  Safety Gate: No previous model. Initial deployment authorized.")

        if not should_deploy:
            return

        # 12. Save artifacts
        version = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        joblib.dump(pipeline, MODELS_DIR / f"feature_pipeline_{version}.joblib")
        joblib.dump(regressor, MODELS_DIR / f"regressor_{version}.joblib")
        joblib.dump(classifier, MODELS_DIR / f"classifier_{version}.joblib")
        joblib.dump(explainer, MODELS_DIR / f"shap_explainer_{version}.joblib")

        manifest = {
            "version": version,
            "pipeline": f"feature_pipeline_{version}.joblib",
            "regressor": f"regressor_{version}.joblib",
            "classifier": f"classifier_{version}.joblib",
            "explainer": f"shap_explainer_{version}.joblib",
            "feature_bounds": feature_bounds,
            "metrics": {"mae": mae, "rmse": rmse, "f1": f1},
            "trained_at": datetime.now(UTC).isoformat(),
        }
        with open(MODELS_DIR / "latest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Training complete! Model version {version} promoted to latest.")

        # 13. Log metrics to DB
        try:
            feature_importance = dict(zip(FEATURE_NAMES, [float(x) for x in regressor.feature_importances_]))
            metric_record = ModelMetric(
                model_version=version,
                mae=mae,
                rmse=rmse,
                f1_weighted=f1,
                parameters=regressor.get_params(),
                feature_importance=feature_importance,
            )
            db.add(metric_record)
            await db.commit()
            print("✅ Metrics saved to database.")
        except Exception as e:
            print(f"⚠️  Could not save metrics to DB (non-fatal): {e}")


if __name__ == "__main__":
    asyncio.run(train_model())
