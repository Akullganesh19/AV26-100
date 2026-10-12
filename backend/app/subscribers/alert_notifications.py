import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.core.events import event_bus

logger = logging.getLogger(__name__)

async def notify_users_of_alert(alert_id, district_id, disease, risk_score, **kwargs):
    async with SessionLocal() as db:
        query = select(User).join(User.districts).where(
            District.id == district_id,
            User.email_alerts == True,
            User.alert_threshold <= (risk_score * 100)
        )
        result = await db.execute(query)
        users = result.scalars().all()

        for user in users:
            await send_notification(user.id, user.email, alert_id, district_id, disease, risk_score)

async def send_notification(user_id, email, alert_id, district_id, disease, risk_score):
    logger.info(f"Targeted Alert dispatched to user {email} (user_id={user_id}) for alert {alert_id} (disease: {disease}, risk: {risk_score})")

def setup_subscribers():
    event_bus.subscribe("alert.triggered", notify_users_of_alert)
    logger.info("Alert notifications subscriber registered.")
