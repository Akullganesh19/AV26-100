import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.events.bus import event_bus
from app.connections.alert_routing import route_alert_to_interested_users, init_connections
from app.models.user import User

@pytest.mark.asyncio
async def test_synapse_connection():
    # Setup connection
    init_connections()
    assert route_alert_to_interested_users in event_bus._listeners["alert.triggered"]

    # Mock route_alert_to_interested_users for emitting
    with patch("app.connections.alert_routing.route_alert_to_interested_users", new_callable=AsyncMock) as mock_route:
        event_bus._listeners["alert.triggered"] = [mock_route]

        event_bus.emit("alert.triggered", alert_id="123", district_id="456", disease="dengue", risk_score=0.8, alert_type="autonomous")

        # Give event loop time to run background task
        await asyncio.sleep(0.1)

        mock_route.assert_called_once_with(alert_id="123", district_id="456", disease="dengue", risk_score=0.8, alert_type="autonomous")
