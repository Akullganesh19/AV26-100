import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
import asyncio

from app.core.events import event_bus
from app.services.notification_dispatch import handle_alert_created


@pytest.fixture(autouse=True)
def setup_event_bus():
    # Make sure tests run isolated
    event_bus._subscribers = {}
    event_bus.subscribe("alert.created", handle_alert_created)
    yield
    event_bus._subscribers = {}


@pytest.mark.asyncio
async def test_alert_created_dispatch():
    district_id = str(uuid4())
    alert_id = str(uuid4())

    payload = {
        "alert_id": alert_id,
        "district_id": district_id,
        "disease": "dengue",
        "risk_score": 0.85,
        "alert_type": "autonomous",
    }

    class MockUser:
        def __init__(self, email, name):
            self.email = email
            self.name = name

    class MockDistrict:
        def __init__(self, name):
            self.name = name

    class MockScalars:
        def all(self):
            return [MockUser("test@example.com", "Test User")]

    class MockResultUsers:
        def scalars(self):
            return MockScalars()

    class MockResultDistrict:
        def scalar_one_or_none(self):
            return MockDistrict("Test District")

    mock_db_session = AsyncMock()
    mock_db_session.execute.side_effect = [
        MockResultUsers(),  # First query: affected users
        MockResultDistrict(),  # Second query: district
    ]

    with patch(
        "app.services.notification_dispatch.SessionLocal",
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_db_session), __aexit__=AsyncMock()
        ),
    ):
        with patch(
            "app.services.notification_dispatch.send_alert_notification",
            new_callable=AsyncMock,
        ) as mock_send:
            # Publish event and give it a tiny bit of time to execute background tasks
            await event_bus.publish("alert.created", payload)
            await asyncio.sleep(0.1)

            mock_db_session.execute.assert_called()
            mock_send.assert_called_once_with(
                alert_id=alert_id,
                district_name="Test District",
                disease="dengue",
                risk_score=0.85,
                user_email="test@example.com",
                user_name="Test User",
            )
