import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification
from app.core.events import event_bus

logger = logging.getLogger(__name__)

async def handle_alert_triggered(event_data: dict):
    district_id = event_data.get("district_id")
    risk_score = event_data.get("risk_score", 0.0)
    alert_id = event_data.get("alert_id")
    disease = event_data.get("disease", "Unknown")

    if not district_id:
        return

    logger.info(f"SYNAPSE: Notification subscriber received alert.triggered for district {district_id} with score {risk_score}")

    async with SessionLocal() as db:
        try:
            query = (
                select(User, District)
                .join(User.districts)
                .where(District.id == district_id)
                .where(User.email_alerts == True)
                .where(User.alert_threshold <= (risk_score * 100))
            )
            result = await db.execute(query)

            for user, district in result.all():
                logger.info(f"SYNAPSE: Routing targeted alert {alert_id} to user {user.email}")
                await send_alert_notification(
                    alert_id=str(alert_id),
                    district_name=district.name,
                    disease=disease,
                    risk_score=risk_score,
                    target_email=user.email
                )
        except Exception as e:
            logger.error(f"Error processing notification subscribers: {e}", exc_info=True)

def register_subscribers():
    event_bus.subscribe("alert.triggered", handle_alert_triggered)
    logger.info("Registered notification subscribers")
