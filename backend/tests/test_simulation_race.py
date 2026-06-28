import pytest
import asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import Base, engine
import app.models  # load all to fix mapper
from app.models.scenario import Scenario, SimulationState
from app.models.user import User
from app.services.simulation_service import SimulationService
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_advance_day_race_condition():
    # Setup test DB using fresh tables for the test to avoid foreign key issues from migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Wait, we need to mock or ensure the scenario events don't fail, but let's just test advance_day basic increment
    async with AsyncSessionLocal() as db_session:
        user_id = uuid.uuid4()
        user = User(id=user_id, name="Test User", email=f"test_{uuid.uuid4()}@test.com", password_hash="hash")
        db_session.add(user)

        scenario_id = uuid.uuid4()
        scenario = Scenario(id=scenario_id, name="Test Scenario", description="Test", total_days=10, is_template=True)
        db_session.add(scenario)

        await db_session.commit()

        sim = await SimulationService.create_simulation(db_session, str(scenario_id), str(user_id))
        sim_id = str(sim.id)

    async def advance_task():
        async with AsyncSessionLocal() as session:
            await SimulationService.advance_day(session, sim_id)

    tasks = [advance_task() for _ in range(5)]
    await asyncio.gather(*tasks)

    # Check the actual day now
    async with AsyncSessionLocal() as db_session:
        result = await db_session.execute(select(SimulationState).where(SimulationState.id == sim_id))
        updated_sim = result.scalar_one()

    # The drift risk: multiple workers read current_day (0), add 1, and write back 1.
    # The actual result will probably be 1 instead of 5, OR could be random (1-5).
    # If the system is safe from race conditions, we'll see exactly 5.
    assert updated_sim.current_day == 5, f"Expected day 5, got {updated_sim.current_day}"
