from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import String, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    trained_at: Mapped[datetime] = mapped_column(server_default=func.now())
    mae: Mapped[float] = mapped_column(Numeric(10, 4))
    rmse: Mapped[float] = mapped_column(Numeric(10, 4))
    f1_score: Mapped[float] = mapped_column(Numeric(10, 4))
    parameters: Mapped[dict] = mapped_column(JSON)
    feature_importance: Mapped[dict] = mapped_column(JSON)

if TYPE_CHECKING:
    from .user import User
    from .district import District
    from .prediction import Prediction
    from .alert import Alert
    from .raw_data import RawData
    from .environmental_data import EnvironmentalData
    from .vaccination_coverage import VaccinationCoverage
    from .pipeline_run import PipelineRun
    from .scenario import Scenario, SimulationState, ScenarioEvent
    from .password_reset_token import PasswordResetToken
