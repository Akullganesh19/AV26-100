import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.alert import Alert
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Intelligence emerged: Alerts system now talks to Auth/Users system to route
    notifications only to users who care about this district, have email_alerts enabled,
    and have a threshold below the alert's risk_score.
    """
    try:
        async with SessionLocal() as db:
            # Find users who monitor this district and want alerts
            query = (
                select(User)
                .where(
                    User.districts.any(id=district_id),
                    User.is_active == True,
                    User.email_alerts == True,
                    User.alert_threshold <= (risk_score * 100)
                )
            )
            result = await db.execute(query)
            affected_users = result.scalars().all()

            for user in affected_users:
                # Dispatches notification for each relevant user (simulated)
                logger.info(f"Routing alert {alert_id} for {disease} to user {user.email}")
                await send_alert_notification(
                    alert_id=alert_id,
                    district_name=str(district_id), # Ideally load name, but string ID fine for simulation
                    disease=disease,
                    risk_score=risk_score
                )
    except Exception as e:
        logger.error(f"Error in alert_notification_bridge: {e}", exc_info=True)

# Register listener
event_bus.subscribe("alert.triggered", route_alert_to_users)
logger.info("Synapse: Alert ↔ User bridge established.")
