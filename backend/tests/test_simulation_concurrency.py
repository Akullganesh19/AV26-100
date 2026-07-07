import pytest
import asyncio
from sqlalchemy import select
from app.services.simulation_service import SimulationService

# Ensure all models are loaded
from app.models import Base
from app.models.scenario import Scenario, SimulationState
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
from app.models.audit_log import PredictionAuditLog
from app.models.model_metric import ModelMetric

@pytest.mark.asyncio
async def test_advance_day_concurrency(db_session):
    # 1. Setup Scenario & User
    user = User(
        name="Test User",
        email="test_sim@example.com",
        role="officer"
    )
    db_session.add(user)
    await db_session.commit()

    scenario = Scenario(
        name="Test Scenario",
        description="Test",
        total_days=10
    )
    db_session.add(scenario)
    await db_session.commit()

    # 2. Setup Simulation
    sim = await SimulationService.create_simulation(db_session, str(scenario.id), str(user.id))

    # 3. Simulate 5 concurrent requests to advance day
    async def advance_task():
        # Use a separate DB session for each concurrent request
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import SessionLocal
        async with SessionLocal() as session:
            return await SimulationService.advance_day(session, str(sim.id))

    tasks = [advance_task() for _ in range(5)]
    await asyncio.gather(*tasks)

    # 4. Check final day
    await db_session.refresh(sim)
    assert sim.current_day == 5, f"Expected 5, got {sim.current_day}"
