import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys

# Mock IntegrationService before importing subscribers
mock_integration_service = AsyncMock()
mock_integrations_module = MagicMock()
mock_integrations_module.integration_service = mock_integration_service
sys.modules['app.api.integrations'] = mock_integrations_module

from app.core.events import event_bus
from app.models.alert import Alert, AlertType, AlertStatus
from app.models.user import User, UserRole
from app.models.district import District
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.subscribers import notify_users_on_alert

@pytest.mark.asyncio
async def test_alert_insertion_publishes_event(db_session: AsyncSession):
    # Create test data
    district = District(
        name="Test District",
        state="Test State",
        state_code="TS",
        latitude=0.0,
        longitude=0.0,
        population=1000,
        area_km2=10.0
    )
    db_session.add(district)
    await db_session.commit()

    user1 = User(
        name="User 1",
        email="user1@example.com",
        role=UserRole.OFFICER,
        email_alerts=True,
    )
    user2 = User(
        name="User 2",
        email="user2@example.com",
        role=UserRole.OFFICER,
        email_alerts=False,
    )
    user1.districts.append(district)
    user2.districts.append(district)
    db_session.add_all([user1, user2])
    await db_session.commit()

    # Track published events
    published_events = []

    def test_subscriber(*args, **kwargs):
        published_events.append(kwargs)

    event_bus.subscribe('alert.triggered', test_subscriber)

    # Insert alert to trigger the event hook
    alert = Alert(
        district_id=district.id,
        disease="COVID-19",
        risk_score=0.85,
        alert_type=AlertType.AUTONOMOUS,
        status=AlertStatus.TRIGGERED
    )
    db_session.add(alert)
    await db_session.commit()

    # Verify event was published and captured by test subscriber
    assert len(published_events) == 1
    event_data = published_events[0]
    assert event_data['district_id'] == str(district.id)
    assert event_data['disease'] == "COVID-19"
    assert event_data['risk_score'] == 0.85
    assert event_data['alert_id'] == str(alert.id)

    # Call notify_users_on_alert manually because we don't have a reliable way to wait for the background task created by the hook in a synchronous test without an asyncio loop trick
    # Specifically, the EventBus creates an asyncio task for the subscriber, which runs independently.
    # To properly test the subscriber logic without flakiness:
    mock_integration_service.send_health_alert_email.reset_mock()

    with patch('app.core.subscribers.SessionLocal') as mock_session_local:
        # Give the subscriber its own session to use by mocking SessionLocal
        mock_session_local.return_value.__aenter__.return_value = db_session

        await notify_users_on_alert(
            alert_id=str(alert.id),
            district_id=str(district.id),
            disease="COVID-19",
            risk_score=0.85
        )

    # Verify that send_health_alert_email was called only for user1 (email_alerts=True)
    assert mock_integration_service.send_health_alert_email.call_count == 1
    mock_integration_service.send_health_alert_email.assert_called_once_with(
        to_email="user1@example.com",
        district_name="Test District",
        disease="COVID-19",
        risk_score=0.85
    )
