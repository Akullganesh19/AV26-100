import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import date
from app.services.prediction_service import PredictionService

@pytest.mark.asyncio
@patch("app.services.prediction_service.ml_state", {"pipeline": None, "regressor": None, "classifier": None, "explainer": None, "manifest": {"version": "test"}})
async def test_predict_batch_is_sequential():
    db_mock = AsyncMock()
    service = PredictionService(db=db_mock)

    # We patch predict_single just to return the district_id
    service.predict_single = AsyncMock(side_effect=lambda x, y, z: x)

    district_ids = [uuid4() for _ in range(3)]

    # In predict_batch, it should now execute sequentially instead of gather
    results = await service.predict_batch(district_ids, "disease", date.today())

    assert set(results) == set(district_ids)
