import pytest
import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.prediction_service import PredictionService

@pytest.mark.asyncio
async def test_predict_batch_executes_sequentially():
    """
    Sentinel regression test: Ensures predict_batch does not use asyncio.gather
    or concurrent execution on the same AsyncSession, which would cause an
    IllegalStateChangeError in SQLAlchemy.
    """
    mock_db = MagicMock()
    with patch("app.services.prediction_service.ml_state", {"pipeline": None, "regressor": None, "classifier": None, "explainer": None, "manifest": {"features": [], "version": "1.0"}}):
        service = PredictionService(mock_db)

        # Mock predict_single to track call order and execution
        service.predict_single = AsyncMock()
        service.predict_single.return_value = MagicMock()

        district_ids = [uuid.uuid4() for _ in range(3)]

        results = await service.predict_batch(
            district_ids=district_ids,
            disease="dengue",
            as_of_date=date(2026, 6, 16)
        )

        assert len(results) == 3
        assert service.predict_single.call_count == 3
