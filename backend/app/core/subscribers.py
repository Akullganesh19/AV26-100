import asyncio
import uuid
import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.api.integrations import integration_service
from app.core.events import event_bus

logger = logging.getLogger(__name__)

async def notify_users_of_alert(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Subscribes to 'alert.triggered' events.
    Finds users subscribed to the district with a matching alert threshold and sends an email.
    """
    logger.info(f"Synapse Event Received: Processing alert {alert_id} for district {district_id}")

    await asyncio.sleep(0.1)
    async with SessionLocal() as session:
        # Find district name
        district_result = await session.execute(
            select(District).where(District.id == uuid.UUID(district_id))
        )
        district = district_result.scalar_one_or_none()
        district_name = district.name if district else "Unknown District"

        # Find users who are linked to this district and have an appropriate threshold
        query = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(
                user_district_association.c.district_id == uuid.UUID(str(district_id)),
                User.email_alerts.is_(True),
                User.alert_threshold <= 100,
                User.is_active.is_(True)
            )
        )
        result = await session.execute(query)
        users = result.scalars().all()


        if not users:
            logger.info(f"Synapse Event: No users matching alert threshold for district {district_id}")
            return

        logger.info(f"Synapse Event: Notifying {len(users)} users for alert {alert_id}")

        # Notify each user
        for user in users:
            try:
                await integration_service.send_health_alert_email(
                    to_email=user.email,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
                logger.info(f"Alert email queued for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send alert email to {user.email}: {e}")

# Register the subscription
event_bus.subscribe("alert.triggered", notify_users_of_alert)
