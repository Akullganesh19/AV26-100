import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from app.core.events import event_bus
import app.connections.user_alerts
from app.connections.user_alerts import on_alert_triggered

@pytest.mark.asyncio
@patch('app.connections.user_alerts.SessionLocal')
@patch('app.connections.user_alerts.send_alert_notification')
async def test_alert_triggered_connection(mock_send_notification, mock_session_local):
    # Setup mock DB session
    mock_session = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session

    # Mock DB results
    # 1. District Name
    mock_district_result = MagicMock()
    mock_district_result.fetchone.return_value = ["Test District"]

    # 2. Users
    mock_users_result = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "user123"
    mock_user.email = "test@example.com"
    mock_users_result.fetchall.return_value = [mock_user]

    mock_session.execute.side_effect = [mock_district_result, mock_users_result]

    # Trigger connection logic directly
    await on_alert_triggered("alert123", "district123", "flu", 0.85)

    # Verify notification fanned out (allow async background task to run)
    await asyncio.sleep(0.1)
    mock_send_notification.assert_called_once_with(
        alert_id="alert123",
        district_name="Test District",
        disease="flu",
        risk_score=0.85
    )
