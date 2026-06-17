import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from sqlalchemy import select
from uuid import uuid4

from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.models.alert import Alert, AlertType, AlertStatus
from app.core.events import event_bus
from app.services.alert_dispatch import setup_alert_dispatch, handle_alert_triggered

@pytest.fixture
def mock_integration_service():
    with patch("app.services.alert_dispatch.integration_service.send_health_alert_email", new_callable=AsyncMock) as mock:
        yield mock

@pytest.mark.asyncio
async def test_alert_dispatch_end_to_end(db_session, mock_integration_service):
    # Register the listener
    setup_alert_dispatch()

    # Create dummy district
    district = District(name="Sector 7G", state="Springfield", population=100, area_km2=10.0, latitude=1.0, longitude=1.0, state_code="SP")
    db_session.add(district)
    await db_session.commit()
    await db_session.refresh(district)

    # Create users
    # User 1: matches all criteria
    user1 = User(
        name="Homer Simpson",
        email="homer@snpp.com",
        clerk_id="clerk_123",
        password_hash="fakehash",
        email_alerts=True,
        alert_threshold=50, # Threshold lower than score (88)
        is_active=True
    )
    user1.districts.append(district)

    # User 2: threshold too high
    user2 = User(
        name="Ned Flanders",
        email="ned@leftorium.com",
        clerk_id="clerk_456",
        password_hash="fakehash",
        email_alerts=True,
        alert_threshold=95, # Threshold higher than score (88)
        is_active=True
    )
    user2.districts.append(district)

    # User 3: email_alerts disabled
    user3 = User(
        name="Carl Carlson",
        email="carl@snpp.com",
        clerk_id="clerk_789",
        password_hash="fakehash",
        email_alerts=False,
        alert_threshold=50,
        is_active=True
    )
    user3.districts.append(district)

    # User 4: different district
    district2 = District(name="Shelbyville", state="Springfield", population=100, area_km2=10.0, latitude=1.0, longitude=1.0, state_code="SP")
    user4 = User(
        name="Shelbyville Manhattan",
        email="shelby@ville.com",
        clerk_id="clerk_000",
        password_hash="fakehash",
        email_alerts=True,
        alert_threshold=50,
        is_active=True
    )
    db_session.add_all([user1, user2, user3, user4, district2])
    await db_session.commit()

    # Create Alert
    alert = Alert(
        district_id=district.id,
        disease="Radiation Sickness",
        risk_score=0.88,
        alert_type=AlertType.AUTONOMOUS,
        status=AlertStatus.TRIGGERED
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # Instead of firing over event_bus which uses its own SessionLocal, we test the handler directly passing it
    # No, we actually modified it so we can patch SessionLocal if we want, but wait, the db_session fixture
    # uses a different database (episense_test_test) than SessionLocal uses (episense_test) unless patched.

    # So we should patch SessionLocal to return db_session!
    with patch("app.services.alert_dispatch.SessionLocal", return_value=db_session):
        # We need to make it an async context manager
        class MockSessionLocal:
            async def __aenter__(self):
                return db_session
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        with patch("app.services.alert_dispatch.SessionLocal", return_value=MockSessionLocal()):
            await handle_alert_triggered(str(alert.id))

    # Verify exactly one dispatch (only user1)
    mock_integration_service.assert_called_once_with(
        to_email="homer@snpp.com",
        district_name="Sector 7G",
        disease="Radiation Sickness",
        risk_score=0.88
    )
