import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.district import District
from app.connections.synapse_bridge import event_bus
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

async def on_alert_triggered(alert_id: str, district_id: str, disease: str, risk_score: float, **kwargs):
    try:
        async with SessionLocal() as db:
            # Find all users subscribed to this district who want alerts and where risk > user threshold
            query = select(User).join(User.districts).where(
                District.id == district_id,
                User.email_alerts == True,
                User.alert_threshold <= (risk_score * 100)
            )
            result = await db.execute(query)
            affected_users = result.scalars().all()

            for user in affected_users:
                logger.info(f"Targeted Alert Routing: Notifying user {user.email} (threshold {user.alert_threshold}) about {disease} in {district_id} (risk: {risk_score*100:.1f})")
                # In a real system, enqueue email/SMS to this specific user here
    except Exception as e:
        logger.error(f"Error in alert routing connection: {e}")

def init_alert_routing():
    event_bus.subscribe("alert.triggered", on_alert_triggered)
    logger.info("Synapse Connection Established: Auth ↔ Alerts")
