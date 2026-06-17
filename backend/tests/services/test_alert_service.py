import pytest
from unittest.mock import AsyncMock, patch

from app.services.alert_service import AlertService

@pytest.mark.asyncio
async def test_evaluate_clinical_cluster_error_handling():
    # Arrange
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("Simulated DB Error")

    district_id = "test_district_123"
    disease = "test_disease"

    with patch("app.services.alert_service.logger") as mock_logger:
        # Act
        await AlertService.evaluate_clinical_cluster(mock_db, district_id, disease)

        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args

        # Check that the first positional argument is the error message
        assert call_args[0][0] == f"MISSION FAILURE: Failed to evaluate clinical cluster for {district_id}"

        # Check keyword arguments
        assert call_args[1]["exc_info"] is True
        assert call_args[1]["extra"] == {"disease": disease, "error": "Simulated DB Error"}
