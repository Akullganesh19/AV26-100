import logging
import uuid
from sqlalchemy import select
from app.core.events import event_bus
from app.models.user import User
from app.models.user_district import user_district_association
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

async def handle_targeted_alert(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Targeted cross-system capability to notify users assigned to a district
    when a high-risk prediction or alert is triggered.
    """
    try:
        if isinstance(district_id, str):
            district_uuid = uuid.UUID(district_id)
        else:
            district_uuid = district_id

        async with SessionLocal() as db:
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(
                    user_district_association.c.district_id == district_uuid,
                    User.email_alerts == True,
                    User.is_active == True,
                    User.alert_threshold <= (risk_score * 100)
                )
            )
            result = await db.execute(query)
            users = result.scalars().all()

            for user in users:
                logger.info(
                    f"Targeted Notification: Sending {disease} risk alert to {user.email} "
                    f"(Role: {user.role}, Threshold: {user.alert_threshold})"
                )
    except Exception as e:
        logger.error(f"Error in targeted notification dispatcher: {e}", exc_info=True)

event_bus.on("prediction.high_risk", handle_targeted_alert)
event_bus.on("alert.triggered", handle_targeted_alert)
