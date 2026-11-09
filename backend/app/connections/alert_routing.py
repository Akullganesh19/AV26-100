import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.events.bus import event_bus

logger = logging.getLogger(__name__)

async def route_alert_to_interested_users(alert_id: str, district_id: str, disease: str, risk_score: float, alert_type: str):
    logger.info(f"SYNAPSE: Routing alert {alert_id} for district {district_id}")

    async with SessionLocal() as db:
        # Get users who are officers in this district and have alerts enabled
        query = (
            select(User)
            .join(User.districts)
            .where(District.id == district_id)
            .where(User.email_alerts == True)
            .where(User.alert_threshold <= (risk_score * 100))
        )
        result = await db.execute(query)
        users = result.scalars().all()

        for user in users:
            # Here we would send real personalized notifications
            # For Synapse connection demonstration, we just log the intelligence emerged
            logger.info(f"SYNAPSE CONNECTION FIRED: Auth ↔ Alerts. User {user.email} (Threshold {user.alert_threshold}) notified about {disease} alert ({risk_score*100}) in district {district_id}")

def init_connections():
    event_bus.on("alert.triggered", route_alert_to_interested_users)
