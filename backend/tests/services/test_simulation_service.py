import pytest
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.simulation_service import SimulationService
from app.models.scenario import Scenario, SimulationState
from app.models.user import User

@pytest.mark.asyncio
async def test_advance_day_concurrency(db_session: AsyncSession):
    # Setup test data
    user = User(name="Test User", email="test@test.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    scenario = Scenario(name="Test Scenario", total_days=14, description="Test")
    db_session.add(scenario)
    await db_session.flush()

    sim = SimulationState(scenario_id=scenario.id, user_id=user.id, current_day=0, is_active=True)
    db_session.add(sim)
    await db_session.commit()

    sim_id = sim.id

    # We need separate database sessions to simulate actual concurrency
    from tests.conftest import TEST_DATABASE_URL
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def concurrent_advance():
        async with async_session_maker() as session:
            await SimulationService.advance_day(session, str(sim_id))

    # Run the same operation twice concurrently
    await asyncio.gather(
        concurrent_advance(),
        concurrent_advance()
    )

    # Verify the result
    async with async_session_maker() as session:
        query = select(SimulationState).where(SimulationState.id == sim_id)
        result = await session.execute(query)
        final_sim = result.scalar_one()

        # If it was 0, and we advanced twice concurrently, what should it be?
        # A true atomic operation (if they run sequentially via locks) would make it 2.
        # But if it's supposed to just "advance one day", wait, is it advancing based on a button click?
        # Yes, clicking "Advance Day" might happen twice. It shouldn't double-advance from one user intent,
        # but realistically the current code is a classic read-modify-write race condition:
        # sim = db.execute(select...); sim.current_day += 1; db.commit()
        # So concurrently, they both read 0, and both set it to 1.
        # But if we lock it via `with_for_update()`, it will serialize, and one will set to 1, the next to 2.
        # Actually, let's see.
        print(f"Final sim day: {final_sim.current_day}")

        assert final_sim.current_day == 2
