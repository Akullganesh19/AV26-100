import logging
import asyncio
from app.core.events import event_bus
from app.core.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def handle_high_risk_prediction(prediction_data: dict):
    """
    Subscribes to 'prediction.high_risk' events.
    Enriches the event with targeted user data (Auth system)
    and sends personalized alerts (Notification system).
    """
    district_id = prediction_data.get("district_id")
    disease = prediction_data.get("disease")
    risk_score = prediction_data.get("risk_score")
    alert_id = prediction_data.get("prediction_id")

    if not all([district_id, disease, risk_score, alert_id]):
        logger.error("Missing data in prediction.high_risk event")
        return

    async with SessionLocal() as db:
        # Find all active users who:
        # 1. Have email alerts enabled
        # 2. Have an alert threshold <= the current risk score
        # 3. Are assigned to this district
        query = select(User).where(
            User.is_active == True,
            User.email_alerts == True,
            User.alert_threshold <= int(risk_score)
        ).options(selectinload(User.districts))

        result = await db.execute(query)
        users = result.scalars().all()

        notified_users = 0
        tasks = set()

        # Keep strong reference to tasks to avoid GC
        if not hasattr(handle_high_risk_prediction, '_tasks'):
            handle_high_risk_prediction._tasks = set()

        for user in users:
            # Check if user is in this district
            user_district_ids = [str(d.id) for d in user.districts]
            if str(district_id) in user_district_ids:
                # Trigger personalized notification
                # We need to maintain a strong reference to these tasks if we create them here
                task = asyncio.create_task(
                    send_alert_notification(
                        alert_id=f"{alert_id}-{user.id}",
                        district_name=f"District {district_id} (Targeted to {user.name})",
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email  # Need to modify send_alert_notification to accept user_email
                    )
                )
                handle_high_risk_prediction._tasks.add(task)
                task.add_done_callback(handle_high_risk_prediction._tasks.discard)
                notified_users += 1

        logger.info(f"Targeted alerts dispatched to {notified_users} users for district {district_id}")

event_bus.subscribe("prediction.high_risk", handle_high_risk_prediction)
