import pytest
import uuid
from sqlalchemy import select
from app.models.user import User, UserRole
from app.models.district import District
from app.models.alert import Alert, AlertType, AlertStatus
from app.services.notification_dispatcher import dispatch_targeted_alerts
from app.models.user_district import user_district_association
import app.tasks.alerts as alert_tasks

@pytest.mark.asyncio
async def test_dispatch_targeted_alerts(db_session, mocker):
    # Mock the send_alert_notification function to check if it's called properly
    mock_send_alert = mocker.patch.object(alert_tasks, 'send_alert_notification')

    # Setup Data
    district_id = uuid.uuid4()
    district = District(
        id=district_id,
        name="Test District",
        state="TS",
        state_code="TS",
        latitude=0.0,
        longitude=0.0,
        population=1000,
        area_km2=10.0
    )
    db_session.add(district)

    # User 1: Should receive (threshold 70, score 80)
    user1_id = uuid.uuid4()
    user1 = User(
        id=user1_id,
        email="u1@test.com",
        name="User 1",
        role=UserRole.OFFICER,
        alert_threshold=70,
        email_alerts=True,
        is_active=True
    )
    db_session.add(user1)

    # User 2: Should NOT receive (threshold 90, score 80)
    user2_id = uuid.uuid4()
    user2 = User(
        id=user2_id,
        email="u2@test.com",
        name="User 2",
        role=UserRole.OFFICER,
        alert_threshold=90,
        email_alerts=True,
        is_active=True
    )
    db_session.add(user2)

    await db_session.commit()

    # Add users to district
    db_session.add(district) # Re-add to session
    district.users.append(user1)
    district.users.append(user2)
    await db_session.commit()

    alert_id = uuid.uuid4()
    alert = Alert(
        id=alert_id,
        district_id=district_id,
        disease="Test Disease",
        risk_score=0.80, # 80%
        alert_type=AlertType.AUTONOMOUS,
        status=AlertStatus.TRIGGERED
    )
    db_session.add(alert)
    await db_session.commit()

    # Dispatch alerts
    await dispatch_targeted_alerts(db_session, alert, "Test District")

    # Assert
    # It should only be called once, for user1
    assert mock_send_alert.call_count == 1
    mock_send_alert.assert_called_with(
        alert_id=str(alert_id),
        district_name="Test District",
        disease="Test Disease",
        risk_score=0.80,
        user_id=str(user1_id)
    )
