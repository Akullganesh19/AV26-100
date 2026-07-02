import logging
from app.core.events import event_bus
from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification
from email.mime.text import MIMEText
# We will use logging instead of send_alert_notification directly if we want to send to each user
# but let's see how send_alert_notification is implemented.

logger = logging.getLogger(__name__)

async def on_alert_created(event_data: dict):
    """
    Subscribes to 'alert.created'.
    Finds the relevant district and all users assigned to it who
    want email alerts and whose threshold is met by the new alert's risk_score.
    """
    try:
        district_id = event_data["district_id"]
        disease = event_data["disease"]
        risk_score = float(event_data.get("risk_score", 0.0))
        alert_id = str(event_data["id"])

        async with SessionLocal() as db:
            # Get district name
            district_result = await db.execute(select(District).where(District.id == district_id))
            district = district_result.scalar_one_or_none()
            district_name = district.name if district else "Unknown District"

            # Query relevant users
            # User must belong to the district, want email alerts, and the risk must meet/exceed their threshold
            risk_percentage = risk_score * 100
            user_query = select(User).where(
                User.districts.any(id=district_id),
                User.email_alerts == True,
                User.alert_threshold <= risk_percentage
            )
            users_result = await db.execute(user_query)
            target_users = users_result.scalars().all()

            for user in target_users:
                # We log that we are notifying a specific user.
                # In a real system, send_alert_notification would take the user.email
                logger.info(
                    f"Targeting user {user.email} for alert {alert_id}",
                    extra={
                        "user_email": user.email,
                        "district": district_name,
                        "disease": disease,
                        "risk_score": risk_score
                    }
                )

            # Since the current signature of send_alert_notification only notifies the "Jurisdiction Monitor" generically,
            # we invoke it ONCE if there are ANY targeted users, passing the district_name to avoid N+1 spam.
            if target_users:
                logger.info(f"Triggering generalized alert notification for district {district_name} due to active user subscriptions.")
                await send_alert_notification(
                    alert_id=alert_id,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
    except Exception as e:
        logger.error(f"Failed to process alert.created event: {e}", exc_info=True)

# Register the subscriber
event_bus.subscribe("alert.created", on_alert_created)
logger.info("Registered subscribers on the Event Bus.")
