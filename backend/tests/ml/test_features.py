import pytest
import uuid
from datetime import date, timedelta
from sqlalchemy import insert
from app.ml.features import FeatureBuilder, FEATURE_NAMES
from app.models.raw_data import RawData, DataSource
from app.models.district import District

@pytest.mark.asyncio
async def test_feature_pipeline_sql_lags(db_session):
    # 1. Setup: Create a district
    district_id = uuid.uuid4()
    await db_session.execute(
        insert(District).values(
            id=district_id,
            name="Test District",
            state="Test State",
            state_code="TS",
            latitude=12.97,
            longitude=77.59,
            population=1000000,
            area_km2=500
        )
    )

    # 2. Setup: Seed 8 weeks of case data (growing linear trend)
    # week 1: 10, week 2: 20, ... week 8: 80
    base_date = date(2024, 1, 1)
    for i in range(8):
        await db_session.execute(
            insert(RawData).values(
                id=uuid.uuid4(),
                district_id=district_id,
                disease="cholera",
                week_start_date=base_date + timedelta(weeks=i),
                confirmed_cases=(i + 1) * 10,
                source=DataSource.IHIP
            )
        )
    await db_session.commit()

    # 3. Execution: Build features for Week 8
    builder = FeatureBuilder(db_session)
    # Target date: Week 8 (2024-02-19)
    target_date = base_date + timedelta(weeks=7)
    df = await builder.build(district_id, "cholera", target_date)

    # 4. Verification
    assert df is not None
    assert len(df) == 1
    row = df.iloc[0]

    # Week 8 cases = 80
    # Lag 1 should be Week 7 cases = 70
    assert row["confirmed_cases_lag1"] == 70
    # Lag 4 should be Week 4 cases = 40
    assert row["confirmed_cases_lag4"] == 40
    
    # 4-week rolling mean (Weeks 5, 6, 7, 8) -> (50+60+70+80)/4 = 65.0
    assert float(row["cases_rolling_mean_4wk"]) == 65.0
    
    # Verify standard deviation is calculated (not null)
    assert row["cases_rolling_std_4wk"] > 0
