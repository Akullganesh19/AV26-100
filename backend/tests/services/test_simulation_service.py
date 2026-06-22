import asyncio
import uuid
import pytest
import pytest_asyncio
import datetime
from sqlalchemy import select

import app.models
from app.models.scenario import Scenario, SimulationState
from app.models.user import User
from app.services.simulation_service import SimulationService
from app.core.database import SessionLocal, Base, engine

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_advance_day_concurrency():
    """Test that concurrent advance_day calls do not cause current_day to drift."""

    # 1. Setup mock data
    async with SessionLocal() as db:
        user = User(id=uuid.uuid4(), name="Test User", email="ledger_test@example.com", is_active=True, password_hash="pw")
        db.add(user)

        scenario = Scenario(id=uuid.uuid4(), name="Test Scenario", description="Desc", total_days=5)
        db.add(scenario)
        await db.commit()

        sim = SimulationState(
            id=uuid.uuid4(),
            scenario_id=scenario.id,
            user_id=user.id,
            current_day=0,
            is_active=True
        )
        db.add(sim)
        await db.commit()
        sim_id = str(sim.id)

    # 2. Fire concurrent advance_day operations
    async def run_advance():
        async with SessionLocal() as session:
            await SimulationService.advance_day(session, sim_id)

    await asyncio.gather(run_advance(), run_advance(), run_advance())

    # 3. Check the result
    async with SessionLocal() as db:
        query = select(SimulationState).where(SimulationState.id == sim_id)
        result = await db.execute(query)
        sim = result.scalar_one()
        assert sim.current_day == 3, f"Expected 3, got {sim.current_day}. Race condition occurred!"
