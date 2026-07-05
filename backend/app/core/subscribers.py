import logging
from sqlalchemy import select
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def notify_users_of_alert(alert_id: str, district_id: str, district_name: str, disease: str, risk_score: float):
    """
    Listens to 'alert.triggered'. Finds all users assigned to the district,
    who have email alerts enabled, and whose risk threshold is exceeded.
    """
    logger.info(f"Event received: alert.triggered for alert {alert_id}")

    async with SessionLocal() as db:
        # Find users who monitor this district and want alerts
        query = (
            select(User)
            .filter(User.districts.any(id=district_id))
            .where(User.email_alerts == True)
            .where(User.alert_threshold <= (risk_score * 100))
        )
        result = await db.execute(query)
        users = result.scalars().all()

        if not users:
            logger.info(f"No users found meeting notification criteria for alert {alert_id}")
            return

        logger.info(f"Found {len(users)} users to notify for alert {alert_id}")

        for user in users:
            await send_alert_notification(
                alert_id=str(alert_id),
                district_name=district_name,
                disease=disease,
                risk_score=float(risk_score),
                user_email=user.email
            )

# Register the subscriber
event_bus.subscribe("alert.triggered", notify_users_of_alert)
