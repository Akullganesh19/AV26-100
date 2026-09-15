import pytest
from app.tasks.alerts import send_alert_notification
from app.models.user import User, UserRole
from app.models.district import District
from app.models.user_district import user_district_association
import uuid

@pytest.mark.asyncio
async def test_send_alert_notification_targeted(db_session, caplog):
    # Setup test data
    d1 = District(id=uuid.uuid4(), name="Sector 7G", state="State", state_code="ST", latitude=0.0, longitude=0.0, population=1000, area_km2=10.0)
    d2 = District(id=uuid.uuid4(), name="Sector 8", state="State", state_code="ST", latitude=0.0, longitude=0.0, population=1000, area_km2=10.0)

    u1 = User(id=uuid.uuid4(), name="Homer", email="homer@snpp.com", role=UserRole.OFFICER, email_alerts=True, alert_threshold=60)
    u1.districts.append(d1)

    u2 = User(id=uuid.uuid4(), name="Lenny", email="lenny@snpp.com", role=UserRole.OFFICER, email_alerts=True, alert_threshold=90)
    u2.districts.append(d1)

    u3 = User(id=uuid.uuid4(), name="Carl", email="carl@snpp.com", role=UserRole.OFFICER, email_alerts=True, alert_threshold=60)
    u3.districts.append(d2)

    db_session.add_all([d1, d2, u1, u2, u3])
    await db_session.commit()

    with caplog.at_level("INFO"):
        result = await send_alert_notification("alert-1", "Sector 7G", "Flu", 0.75)

    assert "Notifying 1 targeted officers" in caplog.text
    assert "homer@snpp.com" in caplog.text
    assert "lenny@snpp.com" not in caplog.text # Threshold too high (90 > 75)
    assert "carl@snpp.com" not in caplog.text # Wrong district
    assert "homer@snpp.com" in result.get("recipients", [])
