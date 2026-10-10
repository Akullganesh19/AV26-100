import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.core.events import event_bus
from app.tasks.alerts import send_alert_notification
from app.models.user import User, UserRole
from app.models.user_district import user_district_association
from sqlalchemy import select

logger = logging.getLogger(__name__)

async def handle_alert_triggered(alert_id: str, district_id: str, disease: str, risk_score: float, district_name: str = "Unknown District"):
    """
    Subscribes to 'alert.triggered' event.
    Dispatches targeted alerts to relevant officials in the district.
    """
    logger.info(f"Event received: alert.triggered for {disease} in {district_id}")

    async with SessionLocal() as db:
        try:
            # Find users mapped to this district who want email alerts
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(
                    user_district_association.c.district_id == district_id,
                    User.is_active == True,
                    User.email_alerts == True,
                    User.alert_threshold <= (risk_score * 100) # Only alert if risk score is above user's threshold
                )
            )
            result = await db.execute(query)
            users = result.scalars().all()

            if not users:
                logger.info(f"No active subscribers found for alerts in district {district_id}")
                return

            logger.info(f"Dispatching notifications to {len(users)} users for alert {alert_id}")

            for user in users:
                logger.info(f"Notifying {user.email} (Threshold: {user.alert_threshold})")
                await send_alert_notification(
                    alert_id=alert_id,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score,
                    target_email=user.email
                )

        except Exception as e:
            logger.error(f"Failed to process alert.triggered event: {e}", exc_info=True)

def setup_subscribers():
    event_bus.subscribe("alert.triggered", handle_alert_triggered)
