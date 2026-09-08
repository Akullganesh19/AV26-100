import pytest
import asyncio
from uuid import uuid4
from datetime import date
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.prediction_service import PredictionService, ml_state
from app.models.prediction import RiskTier

@pytest.fixture(autouse=True)
def mock_ml_state():
    ml_state["pipeline"] = MagicMock()
    ml_state["regressor"] = MagicMock()
    ml_state["classifier"] = MagicMock()
    ml_state["explainer"] = MagicMock()
    ml_state["manifest"] = {"version": "v1.0"}

@pytest.mark.asyncio
async def test_predict_batch_concurrency():
    db = AsyncMock()
    service = PredictionService(db)

    # Mock predict_single to track calls and return a dummy
    service.predict_single = AsyncMock(return_value="mock_prediction")

    district_ids = [uuid4() for _ in range(3)]
    results = await service.predict_batch(district_ids, "cholera", date.today())

    assert len(results) == 3
    assert service.predict_single.call_count == 3
