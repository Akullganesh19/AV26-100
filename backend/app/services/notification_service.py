import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.user_district import user_district_association
from app.core.events import EventBus

logger = logging.getLogger(__name__)

async def notify_users_of_alert(alert_id: str, district_id: str, risk_score: float, disease: str):
    logger.info(f"NotificationService: Processing alert {alert_id} for district {district_id}")
    async with SessionLocal() as db:
        query = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(user_district_association.c.district_id == district_id)
        )
        result = await db.execute(query)
        users = result.scalars().all()

        for user in users:
            if user.email_alerts and (risk_score * 100) >= user.alert_threshold:
                logger.info(
                    f"INTELLIGENCE EMERGED: Notifying user {user.email} (threshold {user.alert_threshold}) "
                    f"of {disease} alert (risk {risk_score * 100:.1f}) in district {district_id}"
                )
            else:
                logger.debug(
                    f"Skipping user {user.email}: threshold {user.alert_threshold} > risk {risk_score * 100:.1f} "
                    f"or email_alerts is {user.email_alerts}"
                )

def setup_notifications():
    EventBus.subscribe("alert.created", notify_users_of_alert)
