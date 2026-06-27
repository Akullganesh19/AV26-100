import pytest
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.scenario import Scenario, SimulationState
from app.models.user import User
from app.services.simulation_service import SimulationService
from app.core.config import settings
from app.core.database import Base

TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"
engine = create_async_engine(TEST_DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.mark.asyncio
async def test_concurrent_advance_day():
    # Setup test data using a new session
    async with async_session_maker() as db_session:
        # Clean db
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        user = User(
            email="test_ledger@example.com",
            password_hash="fake",
            role="officer",
            name="Ledger Test",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create a scenario
        scenario = Scenario(name="Concurrency Test", description="Test", total_days=14)
        db_session.add(scenario)
        await db_session.commit()
        await db_session.refresh(scenario)

        # Create simulation state
        sim = await SimulationService.create_simulation(db_session, str(scenario.id), str(user.id))
        sim_id = str(sim.id)

    # Run advance_day twice concurrently with two separate connections
    async def worker():
        async with async_session_maker() as session:
            return await SimulationService.advance_day(session, sim_id)

    await asyncio.gather(worker(), worker())

    # Check current_day
    async with async_session_maker() as session:
        query = select(SimulationState).where(SimulationState.id == sim_id)
        result = await session.execute(query)
        final_sim = result.scalar_one()

        assert final_sim.current_day == 2, f"Expected 2, got {final_sim.current_day}"
