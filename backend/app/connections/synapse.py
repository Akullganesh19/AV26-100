import logging
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.models.user import User
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Enrichment/Correlation Pattern:
    Alert system fires an event. This listens and queries the Auth/User system
    to figure out who actually needs to know about it based on thresholds and district.
    """
    logger.info(f"Synapse routing alert {alert_id} for district {district_id}")
    async with SessionLocal() as db:
        # We need users who are subscribed to this district and have a threshold <= risk_score * 100
        # and want email alerts
        query = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(
                and_(
                    user_district_association.c.district_id == district_id,
                    User.email_alerts.is_(True),
                    User.alert_threshold <= (risk_score * 100)
                )
            )
        )
        result = await db.execute(query)
        users = result.scalars().all()

        for user in users:
            # We would typically call an email service here, but we'll use the existing mock
            logger.info(f"Synapse: Forwarding alert {alert_id} to user {user.email}")
            await send_alert_notification(
                alert_id=alert_id,
                district_name=str(district_id), # Just use ID for now or join district
                disease=disease,
                risk_score=risk_score
            )

def setup_synapse_connections(event_bus):
    logger.info("Setting up Synapse connections")
    event_bus.on("alert.triggered", route_alert_to_users)
