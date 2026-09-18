import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys

# Completely mock out the integration_service and its dependencies since it's hardcoded and erroring on import due to config mismatch
mock_integration_service = MagicMock()
mock_integration_service.send_health_alert_email = AsyncMock()
sys.modules['app.api.integrations'] = MagicMock()
sys.modules['app.api.integrations'].integration_service = mock_integration_service

from app.tasks.alerts import correlate_and_notify_users

@pytest.mark.asyncio
@patch("app.tasks.alerts.SessionLocal")
async def test_correlate_and_notify_users(mock_session_local):
    # Setup mock DB session
    mock_db = AsyncMock()

    # Mock the execute result
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [("test1@example.com",), ("test2@example.com",)]
    mock_db.execute.return_value = mock_result

    mock_session_local.return_value.__aenter__.return_value = mock_db

    await correlate_and_notify_users(
        district_id="1234",
        district_name="Test District",
        disease="Malaria",
        risk_score=95.0
    )

    # Verify emails were sent
    assert mock_integration_service.send_health_alert_email.call_count == 2
    mock_integration_service.send_health_alert_email.assert_any_call(
        to_email="test1@example.com",
        district_name="Test District",
        disease="Malaria",
        risk_score=95.0
    )
    mock_integration_service.send_health_alert_email.assert_any_call(
        to_email="test2@example.com",
        district_name="Test District",
        disease="Malaria",
        risk_score=95.0
    )
