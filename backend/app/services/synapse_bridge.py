import logging
from sqlalchemy import text
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.api.integrations import IntegrationService

logger = logging.getLogger(__name__)

async def on_alert_triggered(district_id: str, disease: str, risk_score: float):
    """
    🧠 Synapse Connection: Alerts ↔ Users
    """
    logger.info(f"Synapse Bridge: Evaluating users for {disease} alert in {district_id}")

    async with SessionLocal() as db:
        query = text("""
            SELECT u.email, d.name as district_name
            FROM users u
            JOIN user_districts ud ON u.id = ud.user_id
            JOIN districts d ON d.id = ud.district_id
            WHERE ud.district_id = :district_id
              AND u.email_alerts = true
              AND u.alert_threshold <= :risk_score_percent
        """)

        result = await db.execute(query, {
            "district_id": district_id,
            "risk_score_percent": risk_score * 100
        })
        affected_users = result.fetchall()

        if affected_users:
            service = IntegrationService()
            for user in affected_users:
                logger.info(f"Synapse Bridge: Threshold met. Notifying {user.email}")
                await service.send_health_alert_email(
                    to_email=user.email,
                    district_name=user.district_name,
                    disease=disease,
                    risk_score=risk_score
                )

event_bus.subscribe("alert.triggered", on_alert_triggered)
