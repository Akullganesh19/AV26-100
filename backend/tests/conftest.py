import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings

# Explicitly import all models so that Base.metadata knows about them
from app.models.scenario import Scenario, ScenarioEvent, SimulationState
from app.models.user import User
from app.models.district import District
from app.models.raw_data import RawData
from app.models.environmental_data import EnvironmentalData
from app.models.vaccination_coverage import VaccinationCoverage
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.pipeline_run import PipelineRun
from app.models.model_metric import ModelMetric
from app.models.password_reset_token import PasswordResetToken
from app.models.audit_log import PredictionAuditLog
from app.models.user_district import user_district_association
import app.models

# Use the dedicated test database created in the previous step
TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

@pytest_asyncio.fixture
async def db_session():
    """
    Creates a fresh database session for each test, 
    ensuring loop consistency and data isolation.
    """
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        # Reset schema for each test run
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
    
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session_factory():
    engine = create_async_engine(TEST_DATABASE_URL)
    factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    yield factory
    await engine.dispose()
