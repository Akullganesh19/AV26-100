import pytest
import pytest_asyncio
import asyncio
from sqlalchemy import select, func

from app.models.scenario import Scenario, ScenarioEvent, SimulationState
from app.models.user import User
from app.models.district import District
from app.models.audit_log import PredictionAuditLog
from app.services.simulation_service import SimulationService

# Import association tables or everything from base to make sure relations work
from app.models import Base
from app.models.district import District  # Ensure models module __init__ loads it correctly if needed

@pytest.mark.asyncio
async def test_advance_day_race_condition(db_session):
    # Setup test data
    user = User(email="officer@test.com", name="Officer Test", password_hash="hash")
    db_session.add(user)

    district = District(name="Test District", state="TS", state_code="TS", area_km2=100, population=1000, latitude=12.9, longitude=77.5)
    db_session.add(district)

    scenario = Scenario(name="Test Scenario", description="desc", total_days=10)
    db_session.add(scenario)

    await db_session.flush()

    event = ScenarioEvent(
        scenario_id=scenario.id,
        day_offset=1,
        event_type="CLINICAL_SURGE",
        district_id=district.id,
        disease="dengue",
        data_json={"risk_score": 0.9}
    )
    db_session.add(event)
    await db_session.flush()

    sim = await SimulationService.create_simulation(db_session, str(scenario.id), str(user.id))

    # Assert initial state
    assert sim.current_day == 0
    await db_session.commit() # Commit so other sessions can see it!

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings

    TEST_DATABASE_URL = str(settings.DATABASE_URL) if str(settings.DATABASE_URL).endswith("_test") else str(settings.DATABASE_URL) + "_test"
    engine = create_async_engine(TEST_DATABASE_URL, pool_size=10, max_overflow=20)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def concurrent_advance():
        async with async_session() as session:
            await SimulationService.advance_day(session, str(sim.id))

    # Fire 3 concurrent advance day requests
    await asyncio.gather(
        concurrent_advance(),
        concurrent_advance(),
        concurrent_advance()
    )

    # Re-fetch from DB
    async with async_session() as session:
        query = select(SimulationState).where(SimulationState.id == sim.id)
        result = await session.execute(query)
        updated_sim = result.scalar_one()

        query_audit = select(func.count(PredictionAuditLog.id)).where(PredictionAuditLog.user_id == user.id)
        result_audit = await session.execute(query_audit)
        audit_count = result_audit.scalar()

        print(f"Final sim.current_day: {updated_sim.current_day}")
        print(f"Total audit logs: {audit_count}")

        # The expected output of 3 advances should be current_day = 3.
        # And audit count should be 6 because the surge injects 6 HIGH risk screenings at day_offset 1.
        # Since day 1 is hit exactly once, we should have 6 logs.
        assert updated_sim.current_day == 3
        assert audit_count == 6
