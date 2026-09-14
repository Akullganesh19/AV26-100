import pytest
from unittest.mock import patch, AsyncMock
from app.core.events import event_bus
from app.bridge.alert_notification_bridge import route_alert_to_users
import uuid

@pytest.mark.asyncio
async def test_alert_event_fires_bridge():
    with patch("app.bridge.alert_notification_bridge.route_alert_to_users", new_callable=AsyncMock) as mock_route:
        # Re-subscribe mock for testing
        event_bus.subscribe("test.alert.triggered", mock_route)

        district_id = str(uuid.uuid4())
        alert_id = str(uuid.uuid4())

        # Publish
        event_bus.publish("test.alert.triggered", alert_id=alert_id, district_id=district_id, disease="heart", risk_score=0.90)

        # Yield to event loop
        import asyncio
        await asyncio.sleep(0.1)

        mock_route.assert_called_once_with(alert_id=alert_id, district_id=district_id, disease="heart", risk_score=0.90)
