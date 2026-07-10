import asyncio
import logging
from uuid import UUID
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

@event_bus.on("high_risk_prediction")
async def notify_users_of_alert(alert_id: str, district_id: UUID, disease: str, risk_score: float):
    """
    Subscribes to 'high_risk_prediction' event from prediction_service.
    Uses Event Bridge Pattern to loosely couple Prediction System with Notification System.
    """
    if not hasattr(notify_users_of_alert, "_tasks"):
        notify_users_of_alert._tasks = set()

    async with SessionLocal() as db:
        # Find district name for fallback
        district = await db.get(District, district_id)
        district_name = district.name if district else "Jurisdiction Monitor"

        # Query users who want email alerts, have a threshold <= risk_score, and belong to the district
        # Risk score from model is 0-100 scale, User threshold is 0-100 scale.
        query = (
            select(User)
            .where(User.email_alerts == True)
            .where(User.alert_threshold <= risk_score)
            .where(User.districts.any(District.id == district_id))
        )
        result = await db.execute(query)
        users = result.scalars().all()

        if not users:
            logger.info("No targeted users found for alert dispatch, using generic fallback.")
            task = asyncio.create_task(
                send_alert_notification(
                    alert_id=alert_id,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
            )
            notify_users_of_alert._tasks.add(task)
            task.add_done_callback(notify_users_of_alert._tasks.discard)
        else:
            logger.info(f"Dispatching targeted alert to {len(users)} user(s).")
            for user in users:
                task = asyncio.create_task(
                    send_alert_notification(
                        alert_id=alert_id,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
                )
                notify_users_of_alert._tasks.add(task)
                task.add_done_callback(notify_users_of_alert._tasks.discard)
