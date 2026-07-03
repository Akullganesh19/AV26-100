import logging
from sqlalchemy import select
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def handle_alert_triggered(alert_id: str, district_id: str, disease: str, risk_score: float, district_name: str = "Unknown District"):
    """
    Subscriber that bridges the gap between System A (Alerts) and System B (Auth/Users).
    It dynamically looks up users in the affected district and filters by their personal alert thresholds.
    """
    logger.info(f"Event received: alert.triggered for alert_id={alert_id}")

    # Generic alert so that it's not suppressed if no user matches
    await send_alert_notification(
        alert_id=alert_id,
        district_name=district_name,
        disease=disease,
        risk_score=risk_score
    )

    # Needs to grab a session because it runs in the background triggered by the event bus
    async with SessionLocal() as db:
        try:
            # Query users associated with the district who want alerts
            query = (
                select(User)
                .where(User.districts.any(id=district_id))
                .where(User.email_alerts == True)
            )
            result = await db.execute(query)
            users = result.scalars().all()

            notified_count = 0
            for user in users:
                # Correlate alert threat level against user's specific threshold
                if risk_score * 100 >= user.alert_threshold:
                    # Dynamically personalize the alert
                    await send_alert_notification(
                        alert_id=alert_id,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
                    notified_count += 1

            logger.info(f"Correlated alert {alert_id} with {notified_count} relevant users based on personalized thresholds.")
        except Exception as e:
            logger.error(f"Failed to process alert.triggered event: {e}", exc_info=True)

# Register the subscriber
event_bus.subscribe("alert.triggered", handle_alert_triggered)
