import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification
from app.core.events import event_bus

logger = logging.getLogger(__name__)

async def handle_alert_triggered(alert_id: str, district_id: str, district_name: str, disease: str, risk_score: float):
    """
    Subscribes to 'alert.triggered' and routes targeted notifications to subscribed users.
    """
    async with SessionLocal() as db:
        try:
            # We must ensure district_id matches the DB type (string vs UUID).
            # Convert to string just to be safe if passed as UUID.
            d_id = str(district_id)
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(
                    # using cast to string if needed or just letting sqlalchemy handle it
                    user_district_association.c.district_id == d_id,
                    User.is_active == True,
                    User.email_alerts == True,
                    User.alert_threshold <= risk_score
                )
            )
            result = await db.execute(query)
            users = result.scalars().all()

            logger.info(f"Found {len(users)} users to notify for alert {alert_id} in district {district_id}")
            for user in users:
                await send_alert_notification(
                    alert_id=alert_id,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score,
                    user_email=user.email
                )
        except Exception as e:
            logger.error(f"Failed to handle alert_triggered event: {e}", exc_info=True)

def setup_subscribers():
    event_bus.subscribe("alert.triggered", handle_alert_triggered)
    logger.info("Event subscribers registered")
