from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from typing import List
from sqlalchemy import String, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(512))
    total_days: Mapped[int] = mapped_column(nullable=False, default=14)
    is_template: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    events: Mapped[List["ScenarioEvent"]] = relationship(back_populates="scenario", cascade="all, delete-orphan")
    active_simulations: Mapped[List["SimulationState"]] = relationship(back_populates="scenario")
    user: Mapped["User"] = relationship(secondary="simulation_states", back_populates="scenarios", uselist=False, viewonly=True)
    district: Mapped["District"] = relationship(secondary="scenario_events", back_populates="scenarios", uselist=False, viewonly=True)


class ScenarioEvent(Base):
    __tablename__ = "scenario_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    day_offset: Mapped[int] = mapped_column(nullable=False) # e.g. Day 3 of 14
    event_type: Mapped[str] = mapped_column(String(64), nullable=False) # e.g. "CLINICAL_SURGE", "ENV_ANOMALY"
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), nullable=False)
    disease: Mapped[str] = mapped_column(String(64), nullable=False)
    data_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Relationships
    scenario: Mapped["Scenario"] = relationship(back_populates="events")


class SimulationState(Base):
    """Tracks a user's progress through a specific scenario."""
    __tablename__ = "simulation_states"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    current_day: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_updated: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # Relationships
    scenario: Mapped["Scenario"] = relationship(back_populates="active_simulations")
    user: Mapped["User"] = relationship(back_populates="simulations")

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
