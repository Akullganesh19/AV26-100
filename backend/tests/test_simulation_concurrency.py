import asyncio
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import Base
from app.core.config import settings
from app.models.scenario import Scenario, SimulationState
from app.models.user import User
from app.services.simulation_service import SimulationService

TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

@pytest.mark.asyncio
async def test_simulation_advance_day_concurrency():
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    unique_email = f"sim_test_{uuid.uuid4()}@example.com"

    # Setup initial data
    async with async_session() as session:
        # Create user
        user = User(
            email=unique_email,
            password_hash="pw",
            name="Sim Test",
            role="officer",
            is_active=True
        )
        session.add(user)

        # Create scenario
        scenario = Scenario(
            name="Test Scenario",
            description="A test scenario",
            total_days=5,
            is_template=True
        )
        session.add(scenario)
        await session.commit()
        await session.refresh(user)
        await session.refresh(scenario)

        # Create simulation
        sim = await SimulationService.create_simulation(session, str(scenario.id), str(user.id))
        sim_id = sim.id

    # Concurrently advance day
    async def advance():
        async with async_session() as session:
            await SimulationService.advance_day(session, str(sim_id))

    await asyncio.gather(advance(), advance(), advance(), advance(), advance())

    # Check final state
    async with async_session() as session:
        query = select(SimulationState).where(SimulationState.id == sim_id)
        result = await session.execute(query)
        final_sim = result.scalar_one()

        assert final_sim.current_day == 5, f"Expected current_day to be 5, but got {final_sim.current_day}"

    await engine.dispose()
