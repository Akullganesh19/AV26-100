from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
import enum
from sqlalchemy import String, Integer, Date, ForeignKey, UniqueConstraint, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date

from app.core.database import Base


class DataSource(str, enum.Enum):
    IDSP = "IDSP"
    IHIP = "IHIP"
    MANUAL = "manual"
    SYNTHETIC = "synthetic"


class RawData(Base):
    __tablename__ = "raw_data"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), nullable=False, index=True)
    disease: Mapped[str] = mapped_column(String(64), nullable=False)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    confirmed_cases: Mapped[int] = mapped_column(Integer, default=0)
    suspected_cases: Mapped[int] = mapped_column(Integer, default=0)
    deaths: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[DataSource] = mapped_column(Enum(DataSource), default=DataSource.SYNTHETIC, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    district: Mapped["District"] = relationship(back_populates="raw_data")

    __table_args__ = (
        UniqueConstraint("district_id", "disease", "week_start_date", name="uix_raw_data_district_disease_date"),
        Index("ix_raw_data_district_disease_week", "district_id", "disease", week_start_date.desc()),
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
