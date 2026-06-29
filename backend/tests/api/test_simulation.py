import pytest
import uuid
import asyncio
from httpx import AsyncClient
from sqlalchemy import select
from app.main import app
from app.models.scenario import Scenario, SimulationState
from app.models.user import User

@pytest.mark.asyncio
async def test_simulation_concurrent_advance_day(db_session):
    # Setup test user
    user = User(
        id=uuid.uuid4(),
        name="Test Officer",
        email="officer@episense.test",
        clerk_id="clerk_test",
        is_active=True
    )
    db_session.add(user)

    # Setup scenario
    scenario = Scenario(
        id=uuid.uuid4(),
        name="Test Scenario",
        description="Test Scenario",
        total_days=14,
        is_template=True
    )
    db_session.add(scenario)
    await db_session.commit()

    # Create active simulation
    sim = SimulationState(
        scenario_id=scenario.id,
        user_id=user.id,
        current_day=0,
        is_active=True
    )
    db_session.add(sim)
    await db_session.commit()

    sim_id = sim.id

    from app.services.simulation_service import SimulationService

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.config import settings
    from sqlalchemy.ext.asyncio import create_async_engine

    TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"
    engine = create_async_engine(TEST_DATABASE_URL, pool_size=5)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # To test concurrent access we must use different connections
    async def worker():
        async with async_session() as session:
            await SimulationService.advance_day(session, str(sim_id))

    await asyncio.gather(worker(), worker())

    # Check current day
    # Close previous session's connection and get a fresh connection for assert
    await db_session.close()

    async with async_session() as check_session:
        query = select(SimulationState).where(SimulationState.id == sim_id)
        result = await check_session.execute(query)
        updated_sim = result.scalar_one()
        assert updated_sim.current_day == 2

    await engine.dispose()
