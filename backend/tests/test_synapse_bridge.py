import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import text
from app.services.synapse_bridge import on_alert_triggered
import uuid

@pytest.mark.asyncio
async def test_synapse_bridge_data_flow(db_session):
    district_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    await db_session.execute(text("""
        INSERT INTO districts (id, name, state, state_code, latitude, longitude, population, area_km2)
        VALUES (:id, 'Test District', 'State', 'ST', 0, 0, 1000, 100)
    """), {"id": district_id})

    await db_session.execute(text("""
        INSERT INTO users (id, name, email, role, is_active, alert_threshold, email_alerts)
        VALUES (:id, 'Test User', 'test@example.com', 'OFFICER', true, 80, true)
    """), {"id": user_id})

    await db_session.execute(text("""
        INSERT INTO user_districts (user_id, district_id)
        VALUES (:user_id, :district_id)
    """), {"user_id": user_id, "district_id": district_id})

    await db_session.commit()

    with patch('app.services.synapse_bridge.SessionLocal') as mock_session_local, \
         patch('app.services.synapse_bridge.IntegrationService') as mock_integration_class:

        mock_session_local.return_value.__aenter__.return_value = db_session

        mock_instance = mock_integration_class.return_value
        mock_instance.send_health_alert_email = AsyncMock()

        await on_alert_triggered(district_id, "Flu", 0.85)

        mock_instance.send_health_alert_email.assert_called_once_with(
            to_email='test@example.com',
            district_name='Test District',
            disease='Flu',
            risk_score=0.85
        )
