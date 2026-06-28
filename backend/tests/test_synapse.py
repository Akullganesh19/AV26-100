import asyncio
import sys
import pytest
from unittest.mock import AsyncMock

# Must mock before importing subscribers that initialize the EventBus
mock_integration_service = AsyncMock()
sys.modules['app.api.integrations'] = type('MockModule', (), {'integration_service': mock_integration_service})()

from app.models import Scenario
import app.models
from app.models.user_district import user_district_association
from app.models.user import User, UserRole
from app.models.district import District
from app.models.alert import Alert, AlertStatus, AlertType

from app.core.subscribers import notify_users_of_alert
from app.core.events import event_bus

@pytest.mark.asyncio
async def test_synapse_alert_to_user_notification(db_session):
    # Reset mock
    mock_integration_service.send_health_alert_email.reset_mock()

    # Create District
    district = District(
        name="Synapse Test District",
        state="Test State",
        state_code="TS",
        latitude=0.0,
        longitude=0.0,
        population=100000,
        area_km2=100.0
    )
    db_session.add(district)
    await db_session.commit()
    await db_session.refresh(district)

    # Create User with threshold = 50
    user = User(
        name="Synapse User",
        email="synapse@example.com",
        role=UserRole.OFFICER,
        alert_threshold=50,
        email_alerts=True,
        is_active=True
    )
    db_session.add(user)

    # Assign User to District

    # Assign User to District
    user.districts.append(district)
    await db_session.commit()
    await db_session.refresh(user)


    await asyncio.sleep(0.1)
    # Create Alert with risk_score = 0.88 (88 > 50)
    alert = Alert(
        district_id=district.id,
        disease="Synapse Disease",
        risk_score=0.88,
        status=AlertStatus.TRIGGERED,
        alert_type=AlertType.AUTONOMOUS
    )
    db_session.add(alert)
    await db_session.commit() # This should trigger the after_insert hook

    # Give the async task a moment to run
    await asyncio.sleep(0.2)

    # Assert email was sent
    mock_integration_service.send_health_alert_email.assert_called_once()
    kwargs = mock_integration_service.send_health_alert_email.call_args.kwargs
    assert kwargs["to_email"] == "synapse@example.com"
    assert kwargs["district_name"] == "Synapse Test District"
    assert kwargs["disease"] == "Synapse Disease"
    assert kwargs["risk_score"] == 0.88
