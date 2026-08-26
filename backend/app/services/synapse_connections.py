import logging
from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.user import User
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(alert_id: str, district_id: str, district_name: str, disease: str, risk_score: float):
    """
    Synapse Connection: Auth/Users ↔ Alerts
    Enriches alert payload with affected users based on their alert_threshold.
    """
    logger.info(f"SYNAPSE: Routing alert {alert_id} for {district_name} ({disease}) to relevant users")

    try:
        async with SessionLocal() as db:
            query = select(User).where(
                User.districts.any(id=district_id),
                User.email_alerts.is_(True),
                User.alert_threshold <= (risk_score * 100)
            )
            result = await db.execute(query)
            affected_users = result.scalars().all()

            logger.info(f"SYNAPSE: Found {len(affected_users)} users meeting threshold criteria")

            for user in affected_users:
                 await send_alert_notification(
                     alert_id=alert_id,
                     district_name=district_name,
                     disease=disease,
                     risk_score=risk_score
                 )
                 logger.info(f"SYNAPSE: Dispatched alert to user {user.email}")

    except Exception as exc:
        logger.error(f"SYNAPSE ROUTING FAILED: {str(exc)}", exc_info=True)
