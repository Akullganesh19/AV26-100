import pytest
from unittest.mock import Mock, patch
from app.services.clinical_service import ClinicalService

def test_predict_heart_fallback_to_predict():
    service = ClinicalService()

    mock_model = Mock()
    # predict_proba raises AttributeError
    mock_model.predict_proba.side_effect = AttributeError("Mocked AttributeError")
    # predict returns a specific value
    mock_model.predict.return_value = [0.8]

    service._models["heart"] = mock_model
    service._scalers["heart"] = None

    # Mock _load_model to avoid actually trying to load from file
    with patch.object(service, '_load_model') as mock_load_model:
        # Mock _manifest and _build_response if needed
        service._manifest = {
            "active": {
                "heart": {
                    "version": "v1",
                    "trained_on": "test_data"
                }
            }
        }

        features = [1.0, 2.0, 3.0]
        response = service.predict_heart(features)

        # Verify
        mock_model.predict_proba.assert_called_once()
        mock_model.predict.assert_called_once()

        assert response["disease"] == "heart"
        assert response["risk_score"] == 0.8
        assert response["risk"] is True
