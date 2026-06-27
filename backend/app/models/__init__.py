from __future__ import annotations
from typing import TYPE_CHECKING
from app.core.database import Base
from app.models.user import User
from app.models.district import District
from app.models.raw_data import RawData
from app.models.environmental_data import EnvironmentalData
from app.models.vaccination_coverage import VaccinationCoverage
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.scenario import Scenario
from app.models.pipeline_run import PipelineRun
from app.models.model_metric import ModelMetric
from app.models.password_reset_token import PasswordResetToken
from app.models.audit_log import PredictionAuditLog
from app.models.user_district import user_district_association

__all__ = [
    "Base",
    "user_district_association",
    "User",
    "District",
    "RawData",
    "EnvironmentalData",
    "VaccinationCoverage",
    "Prediction",
    "Alert",
    "Scenario",
    "PipelineRun",
    "PasswordResetToken",
    "PredictionAuditLog",
]

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
