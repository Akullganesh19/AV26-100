import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.user import User
from app.models.scenario import Scenario, SimulationState
from app.services.simulation_service import SimulationService
from app.core.config import settings

# Import association table or module explicitly
from app.models.user_district import user_district_association

db_url_str = str(settings.DATABASE_URL)
if not db_url_str.endswith("_test"):
    TEST_DATABASE_URL = db_url_str + "_test"
else:
    TEST_DATABASE_URL = db_url_str

@pytest.mark.asyncio
async def test_advance_day_concurrency():
    # Setup engine for concurrency
    engine = create_async_engine(TEST_DATABASE_URL, pool_size=5, max_overflow=10)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 1. Setup Data in one session
    async with async_session_maker() as db:
        from app.core.database import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        user = User(name="Test Officer", email="officer_concurrent@test.com", password_hash="hash")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        scenario = Scenario(name="Test Scenario", description="Desc", total_days=10, is_template=True)
        db.add(scenario)
        await db.commit()
        await db.refresh(scenario)

        sim = SimulationState(scenario_id=scenario.id, user_id=user.id, current_day=0, is_active=True)
        db.add(sim)
        await db.commit()
        await db.refresh(sim)

        sim_id = str(sim.id)

    # 2. Fire concurrent advance_day calls
    async def run_advance():
        # Each coroutine gets its own db session to properly simulate concurrency
        async with async_session_maker() as db:
            return await SimulationService.advance_day(db, sim_id)

    # Launch 3 simultaneous requests
    results = await asyncio.gather(*(run_advance() for _ in range(3)), return_exceptions=True)

    # Check for exceptions
    for r in results:
        if isinstance(r, Exception):
            raise r

    # 3. Verify exactly 3 days advanced without skipping or duping
    async with async_session_maker() as db:
        res = await db.execute(select(SimulationState).where(SimulationState.id == sim_id))
        final_sim = res.scalar_one()

        # In a naive increment, concurrent writes will lose some updates
        # So we check what it actually is vs what it should be
        assert final_sim.current_day == 3, f"Expected day 3 due to 3 concurrent advances, got {final_sim.current_day}"

    await engine.dispose()
