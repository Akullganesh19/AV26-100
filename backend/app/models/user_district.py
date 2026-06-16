from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint
from app.core.database import Base

# Association Table for Many-to-Many relationship between Users and Districts
user_district_association = Table(
    "user_districts",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("district_id", ForeignKey("districts.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "district_id", name="uix_user_district")
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
