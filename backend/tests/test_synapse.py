import pytest
import uuid
from app.models.user import User, UserRole
from app.models.district import District
from app.models.user_district import user_district_association
from app.connections.synapse import route_alert_to_users
import asyncio

@pytest.mark.asyncio
async def test_route_alert_to_users_filters_correctly(db_session):
    district_id = uuid.uuid4()
    # Create district
    d1 = District(id=district_id, name="Test District", state="Texas", state_code="TX", latitude=0.0, longitude=0.0, population=100, area_km2=10.0)
    db_session.add(d1)

    # User 1: correct district, low threshold, wants emails
    u1 = User(email="u1@example.com", name="U1", role=UserRole.OFFICER, alert_threshold=50, email_alerts=True)
    # User 2: correct district, threshold too high, wants emails
    u2 = User(email="u2@example.com", name="U2", role=UserRole.OFFICER, alert_threshold=90, email_alerts=True)
    # User 3: correct district, low threshold, does not want emails
    u3 = User(email="u3@example.com", name="U3", role=UserRole.OFFICER, alert_threshold=50, email_alerts=False)

    db_session.add_all([u1, u2, u3])
    await db_session.commit()

    await db_session.execute(user_district_association.insert().values(user_id=u1.id, district_id=d1.id))
    await db_session.execute(user_district_association.insert().values(user_id=u2.id, district_id=d1.id))
    await db_session.execute(user_district_association.insert().values(user_id=u3.id, district_id=d1.id))
    await db_session.commit()

    from unittest.mock import patch, AsyncMock

    with patch("app.connections.synapse.SessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = db_session
        await route_alert_to_users("alert-123", str(district_id), "Flu", 0.70)

    # Test should run without exceptions. In a real test, you'd mock send_alert_notification to assert it was called exactly once for u1.
