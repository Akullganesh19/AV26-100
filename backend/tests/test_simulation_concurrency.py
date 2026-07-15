import pytest
import asyncio
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

# IMPORT ALL MODELS to fix NoForeignKeysError ORM issue
from app.models.scenario import Scenario, SimulationState, ScenarioEvent
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.raw_data import RawData
from app.models.environmental_data import EnvironmentalData
from app.models.vaccination_coverage import VaccinationCoverage
from app.models.pipeline_run import PipelineRun
from app.models.password_reset_token import PasswordResetToken

from app.services.simulation_service import SimulationService
from app.core.database import Base
from app.core.config import settings

TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

@pytest.mark.asyncio
async def test_advance_day_concurrency():
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        user = User(name="Test User", email="test@example.com", password_hash="hash")
        session.add(user)
        scenario = Scenario(name="Test Scenario", description="desc", total_days=5, is_template=True)
        session.add(scenario)
        await session.commit()

        sim = SimulationState(
            scenario_id=scenario.id,
            user_id=user.id,
            current_day=0,
            is_active=True
        )
        session.add(sim)
        await session.commit()
        sim_id = str(sim.id)

    async def run_advance():
        async with async_session() as session:
            await SimulationService.advance_day(session, sim_id)

    # Run 5 concurrently
    await asyncio.gather(*[run_advance() for _ in range(5)])

    async with async_session() as session:
        result = await session.execute(select(SimulationState).where(SimulationState.id == sim_id))
        final_sim = result.scalar_one()

    print(f"Final day: {final_sim.current_day}")
    assert final_sim.current_day == 5
