import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.core.events import event_bus
from app.core.subscribers import handle_high_risk_prediction
from app.models.user import User
from app.models.district import District
import app.models.scenario  # Fix SQLAlchemy generic resolution issue
import app.models.alert
import app.models.password_reset_token
import uuid

@pytest.mark.asyncio
async def test_synapse_event_bus_and_subscriber():
    # Setup mock data
    district_id = uuid.uuid4()

    mock_district = MagicMock(spec=District)
    mock_district.id = district_id

    mock_user = MagicMock(spec=User)
    mock_user.id = uuid.uuid4()
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.districts = [mock_district]

    # Mock DB response
    class MockResult:
        def scalars(self):
            class MockScalars:
                def all(self):
                    return [mock_user]
            return MockScalars()

    mock_db = MagicMock()
    async def mock_execute(*args, **kwargs):
        return MockResult()
    mock_db.execute = mock_execute

    with patch('app.core.subscribers.SessionLocal') as mock_session_local, \
         patch('app.core.subscribers.send_alert_notification') as mock_send:

        # Configure async context manager mock for SessionLocal
        mock_session_context = MagicMock()
        mock_session_context.__aenter__.return_value = mock_db
        mock_session_context.__aexit__.return_value = False
        mock_session_local.return_value = mock_session_context

        # Test direct call to subscriber
        prediction_data = {
            "prediction_id": "pred-123",
            "district_id": str(district_id),
            "disease": "Dengue",
            "risk_score": 85.0
        }

        await handle_high_risk_prediction(prediction_data)

        # Give asyncio tasks a moment to run
        await asyncio.sleep(0.1)

        # Assert send_alert_notification was called with user email
        assert mock_send.call_count == 1
        mock_send.assert_called_with(
            alert_id=f"pred-123-{mock_user.id}",
            district_name=f"District {district_id} (Targeted to Test User)",
            disease="Dengue",
            risk_score=85.0,
            user_email="test@example.com"
        )
