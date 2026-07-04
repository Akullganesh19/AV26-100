import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.services.simulation_service import SimulationService
from app.models.scenario import Scenario, SimulationState
from app.models.user import User
import app.models.user_district
import app.models.alert
import app.models.prediction
import app.models.raw_data
import app.models.environmental_data
import app.models.vaccination_coverage
import app.models.pipeline_run
import app.models.password_reset_token

@pytest.mark.asyncio
async def test_advance_day_concurrency(db_session: AsyncSession, engine):
    user = User(name="Test User", email="test@test.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()

    scenario = Scenario(name="Test Scenario", description="desc", total_days=10)
    db_session.add(scenario)
    await db_session.commit()

    sim = SimulationState(scenario_id=scenario.id, user_id=user.id, current_day=0, is_active=True)
    db_session.add(sim)
    await db_session.commit()
    await db_session.refresh(sim)

    sim_id = str(sim.id)

    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def run_advance():
        async with async_session() as session:
            await SimulationService.advance_day(session, sim_id)

    # Run 5 advances concurrently
    await asyncio.gather(*[run_advance() for _ in range(5)])

    # Verify the result
    async with async_session() as session:
        sim_from_db = await session.get(SimulationState, sim.id)
        # Without locking, it will likely read current_day=0 multiple times, and set to 1.
        # But wait, `current_day += 1` is not an atomic increment.
        # So we assert it's 5. If it's less than 5, the test will fail!
        assert sim_from_db.current_day == 5, f"Expected current_day to be 5, got {sim_from_db.current_day}"
