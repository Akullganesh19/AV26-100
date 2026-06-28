from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
import enum
from sqlalchemy import String, Numeric, Integer, ForeignKey, DateTime, Index, Enum, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base
from app.core.events import event_bus


class AlertStatus(str, enum.Enum):
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertType(str, enum.Enum):
    AUTONOMOUS = "autonomous"
    CLINICAL_CLUSTER = "clinical_cluster"
    ENVIRONMENTAL = "environmental"
    MANUAL = "manual"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), nullable=False, index=True)
    disease: Mapped[str] = mapped_column(String(64), nullable=False)
    risk_score: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.TRIGGERED, nullable=False)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), default=AlertType.AUTONOMOUS, nullable=False)
    
    # Traceability
    prediction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("predictions.id"), nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    
    acknowledged_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    metadata_json: Mapped[str] = mapped_column(String(1024), nullable=True) # Extra info like cluster count

    # Relationships
    district: Mapped["District"] = relationship(back_populates="alerts")
    prediction: Mapped["Prediction"] = relationship(back_populates="alerts")
    acknowledged_by_user: Mapped["User"] = relationship(back_populates="acknowledged_alerts")

    __table_args__ = (
        Index("ix_alert_status_triggered_at", status, triggered_at.desc()),
        # Partial index for acknowledged_by to avoid indexing NULLs
        Index("ix_alert_acknowledged_by", acknowledged_by, postgres_where=(acknowledged_by != None)),
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


@event.listens_for(Alert, "after_insert")
def after_alert_insert(mapper, connection, target):
    event_bus.publish(
        "alert.triggered",
        alert_id=str(target.id),
        district_id=str(target.district_id),
        disease=target.disease,
        risk_score=float(target.risk_score)
    )
