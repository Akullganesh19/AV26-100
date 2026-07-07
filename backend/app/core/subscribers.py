import logging
from sqlalchemy import select
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification
from typing import Any

logger = logging.getLogger(__name__)

async def handle_alert_triggered(
    alert_id: str,
    district_id: str,
    district_name: str,
    disease: str,
    risk_score: float,
    **kwargs: Any
):
    """
    Subscribes to 'alert.triggered' and coordinates cross-system targeted alerts.
    Translates an alert event into specific user notifications via their preferences.
    """
    logger.info(f"Event bus received 'alert.triggered' for {alert_id} in {district_name}")
    async with SessionLocal() as db:
        try:
            # Query users assigned to this district who have email_alerts == True
            # and whose alert threshold is met by this risk score
            # risk_score is typically 0.0-1.0 from predictions/clinical, so * 100 for percentage comparison

            # Need to explicitly import user_districts to avoid registry issues if not already loaded
            from app.models.user_district import user_district_association

            query = select(User).where(
                User.email_alerts == True,
                User.alert_threshold <= int(risk_score * 100),
                User.districts.any(District.id == district_id)
            )

            result = await db.execute(query)
            users = result.scalars().all()

            if not users:
                logger.info(f"No targetable users found for alert {alert_id} in {district_name}")
                return

            import asyncio

            # Maintain a strong reference to prevent garbage collection
            if not hasattr(handle_alert_triggered, "_tasks"):
                handle_alert_triggered._tasks = set()

            for user in users:
                # Dispatch notification per user to third-party integration
                # This could also be a celery task. Currently `send_alert_notification`
                # acts as a coroutine we can call directly.
                task = asyncio.create_task(
                    send_alert_notification(
                        alert_id=alert_id,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
                )
                handle_alert_triggered._tasks.add(task)
                task.add_done_callback(handle_alert_triggered._tasks.discard)

        except Exception as e:
            logger.error(f"Failed to process 'alert.triggered' event: {str(e)}", exc_info=True)


# Register subscribers
event_bus.subscribe("alert.triggered", handle_alert_triggered)

async def handle_prediction_high_risk(
    prediction_id: str,
    district_id: str,
    disease: str,
    risk_score: float,
    **kwargs: Any
):
    """
    Subscribes to 'prediction.high_risk' and delegates to handle_alert_triggered.
    """
    await handle_alert_triggered(
        alert_id=prediction_id,
        district_id=district_id,
        district_name="Jurisdiction Monitor",
        disease=disease,
        risk_score=risk_score
    )

event_bus.subscribe("prediction.high_risk", handle_prediction_high_risk)
