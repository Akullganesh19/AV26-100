import logging
import uuid
from sqlalchemy import select
from app.core.events import event_bus
from app.models.user import User
from app.models.district import District
from app.core.database import SessionLocal
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def handle_alert_triggered(alert_id: str, district_id: str, disease: str, risk_score: float):
    logger.info(f"Listener: Received alert.triggered for {alert_id}")
    async with SessionLocal() as db:
        # Get district name
        try:
            district_uuid = uuid.UUID(str(district_id))
            district_res = await db.execute(select(District).where(District.id == district_uuid))
            district = district_res.scalar_one_or_none()
            district_name = district.name if district else "Unknown District"
        except ValueError:
            district_name = "Unknown District"

        # Find users connected to this district
        try:
            district_uuid = uuid.UUID(str(district_id))
            query = (
                select(User)
                .join(User.districts)
                .where(District.id == district_uuid)
                .where(User.email_alerts == True)
                .where(User.alert_threshold <= risk_score * 100)
                .where(User.is_active == True)
            )
            result = await db.execute(query)
            users = result.scalars().all()

            for user in users:
                logger.info(f"Listener: Dispatching alert to user {user.email}")
                await send_alert_notification(
                    alert_id=str(alert_id),
                    district_name=district_name,
                    disease=disease,
                    risk_score=float(risk_score),
                    user_email=user.email
                )
        except ValueError:
            logger.error(f"Invalid UUID for district_id: {district_id}")

def setup_listeners():
    event_bus.subscribe("alert.triggered", handle_alert_triggered)
