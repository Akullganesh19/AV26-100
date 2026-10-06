import pytest
from app.tasks.alerts import send_alert_notification

@pytest.mark.asyncio
async def test_send_alert_notification():
    result = await send_alert_notification("alert_id_1", "District 1", "disease A", 0.9, "test@example.com")
    assert result["status"] == "dispatched"
    assert result["user_email"] == "test@example.com"
