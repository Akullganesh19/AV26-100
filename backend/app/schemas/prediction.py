from datetime import date
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.ml.features import FEATURE_NAMES
from app.models.prediction import RiskTier


class PredictionRequest(BaseModel):
    district_id: UUID
    disease: str
    prediction_date: date
    overrides: Dict[str, float] = {}

    @field_validator("overrides")
    @classmethod
    def validate_override_keys(cls, v):
        invalid = set(v.keys()) - set(FEATURE_NAMES)
        if invalid:
            raise ValueError(f"Unknown feature names: {invalid}. Supported: {FEATURE_NAMES}")
        return v


class PredictionResponse(BaseModel):
    model_config = {'protected_namespaces': ()}

    prediction_id: UUID
    district_id: UUID
    disease: str
    prediction_date: date
    risk_score: float
    risk_tier: RiskTier
    baseline_score: Optional[float] = None
    delta: Optional[float] = None
    shap_values: Dict[str, float]
    model_version: str
    extrapolation_warning: bool