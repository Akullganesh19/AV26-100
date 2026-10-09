import logging
import uuid
from sqlalchemy import select
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(event_data: dict):
    alert_id = event_data.get("alert_id")
    district_id = event_data.get("district_id")
    disease = event_data.get("disease")
    risk_score = event_data.get("risk_score")

    logger.info(f"Routing alert {alert_id} to relevant users for district {district_id}")

    async with SessionLocal() as db:
        # Cross-system query: Alerts -> Auth (Users)
        stmt = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(user_district_association.c.district_id == uuid.UUID(str(district_id)))
            .where(User.email_alerts == True)
            .where(User.alert_threshold <= (float(risk_score) * 100))
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            logger.info(f"No users configured to receive alert {alert_id}")
            return

        for user in users:
            # Use specific target's identifier per memory guideline
            await send_alert_notification(
                alert_id=str(alert_id),
                district_name=f"District {district_id}",
                disease=disease,
                risk_score=float(risk_score),
                target_email=user.email
            )

def setup_subscribers():
    event_bus.subscribe("alert.created", route_alert_to_users)
