from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
import enum
from typing import Optional
from sqlalchemy import String, Numeric, Date, ForeignKey, JSON, UniqueConstraint, Enum, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date

from app.core.database import Base


class RiskTier(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), nullable=False, index=True)
    pipeline_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("pipeline_runs.id"), index=True)
    disease: Mapped[str] = mapped_column(String(64), nullable=False)
    prediction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_tier: Mapped[RiskTier] = mapped_column(Enum(RiskTier), nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    feature_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    shap_values: Mapped[Optional[dict]] = mapped_column(JSON)
    extrapolation_warning: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    # Relationships
    district: Mapped["District"] = relationship(back_populates="predictions")
    pipeline_run: Mapped["PipelineRun"] = relationship(back_populates="predictions")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="prediction")

    __table_args__ = (
        UniqueConstraint("district_id", "disease", "prediction_date", name="uix_pred_district_disease_date"),
        Index("ix_prediction_district_disease_date", "district_id", "disease", "prediction_date"),
    )

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
