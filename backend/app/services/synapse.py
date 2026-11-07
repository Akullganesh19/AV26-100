import logging
from sqlalchemy import select, and_
from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.district import District
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

async def handle_alert_triggered(district_id: str, disease: str, risk_score: float):
    """Cross-correlates an alert trigger with eligible users."""
    try:
        async with SessionLocal() as db:
            query = (
                select(User, District.name)
                .join(User.districts)
                .where(
                    and_(
                        District.id == district_id,
                        User.email_alerts == True,
                        User.is_active == True,
                        User.alert_threshold <= risk_score * 100
                    )
                )
            )
            result = await db.execute(query)

            for user, district_name in result.all():
                await integration_service.send_health_alert_email(
                    to_email=user.email,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
                logger.info(f"SYNAPSE: Notification dispatched to {user.email} for {disease} in {district_name}")
    except Exception as e:
        logger.error("Failed to cross-correlate alert with users", exc_info=True)

# Wire up the connection
event_bus.on('alert.triggered', handle_alert_triggered)
