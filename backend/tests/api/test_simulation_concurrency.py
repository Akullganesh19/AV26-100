import asyncio
import pytest
from sqlalchemy import select
from app.models.scenario import Scenario, SimulationState
from app.models.user import User
from app.services.simulation_service import SimulationService

@pytest.mark.asyncio
async def test_advance_day_concurrency(db_session, async_session_factory):
    # Setup test data
    user = User(name="Test User", email="test@test.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()

    scenario = Scenario(name="Test Scenario", description="A test scenario", total_days=10)
    db_session.add(scenario)
    await db_session.commit()

    sim = await SimulationService.create_simulation(db_session, str(scenario.id), str(user.id))
    assert sim.current_day == 0

    # Execute advance_day concurrently
    async def concurrent_advance():
        async with async_session_factory() as session:
            return await SimulationService.advance_day(session, str(sim.id))

    tasks = [concurrent_advance() for _ in range(5)]
    await asyncio.gather(*tasks)

    # Refresh sim state
    await db_session.refresh(sim)

    # If correctly locked, the current day should be 5
    assert sim.current_day == 5
