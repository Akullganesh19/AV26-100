import pytest
import uuid
from datetime import datetime
from app.models.alert import Alert, AlertStatus, AlertType
from app.models.district import District
from app.models.user import User, UserRole
from app.services.alert_service import AlertService

@pytest.mark.asyncio
async def test_acknowledge_alert_success(db_session):
    # Setup
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        name="Test User",
        email="testuser@example.com",
        role=UserRole.ADMIN
    )
    db_session.add(user)

    district_id = uuid.uuid4()
    district = District(
        id=district_id,
        name="Test District",
        state="Test State",
        state_code="TS",
        latitude=10.0,
        longitude=20.0,
        population=100000,
        area_km2=500.0
    )
    db_session.add(district)

    alert_id = uuid.uuid4()
    alert = Alert(
        id=alert_id,
        district_id=district_id,
        disease="Flu",
        risk_score=0.9,
        alert_type=AlertType.AUTONOMOUS,
        status=AlertStatus.TRIGGERED
    )
    db_session.add(alert)
    await db_session.commit()

    # Execute
    acknowledged_alert = await AlertService.acknowledge_alert(db_session, str(alert_id), str(user_id))

    # Assert
    assert acknowledged_alert is not None
    assert acknowledged_alert.id == alert_id
    assert acknowledged_alert.status == AlertStatus.ACKNOWLEDGED
    assert acknowledged_alert.acknowledged_by == str(user_id)
    assert acknowledged_alert.acknowledged_at is not None

@pytest.mark.asyncio
async def test_acknowledge_alert_not_found(db_session):
    # Execute
    non_existent_alert_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    result = await AlertService.acknowledge_alert(db_session, non_existent_alert_id, user_id)

    # Assert
    assert result is None
