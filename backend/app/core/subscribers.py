from app.core.events import event_bus
from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.district import District
from app.models.user import User
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification
import logging

logger = logging.getLogger(__name__)

async def route_alerts_to_users(prediction_id, district_id, disease, risk_score):
    async with SessionLocal() as db:
        query = (
            select(District.name, User)
            .join(user_district_association, District.id == user_district_association.c.district_id)
            .join(User, User.id == user_district_association.c.user_id)
            .where(District.id == district_id)
        )
        result = await db.execute(query)
        rows = result.all()

        for row in rows:
            district_name = row.name
            user = row.User
            if user.email_alerts and risk_score >= user.alert_threshold:
                logger.info(f"Routing targeted alert to {user.email} for {disease}")
                await send_alert_notification(
                    alert_id=str(prediction_id),
                    district_name=district_name,
                    disease=disease,
                    risk_score=float(risk_score),
                    target_email=user.email
                )

def setup_subscribers():
    event_bus.subscribe("high_risk_prediction", route_alerts_to_users)
