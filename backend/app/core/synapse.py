import logging
import asyncio
from sqlalchemy import event, select
from app.models.alert import Alert
from app.models.user import User
from app.models.district import District
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

# --- Data Coupling ---
# System A: Alerts (When an alert is inserted into the DB)
# System B: Users (Who receives notifications based on assignment and risk thresholds)

# 1. SQLALchemy Listener to bridge DB -> EventBus
def on_alert_created(mapper, connection, target: Alert):
    """
    Synchronous SQLAlchemy listener that fires *after* an Alert is inserted.
    We convert this DB event into an EventBus message to decouple the systems.
    """
    logger.info(f"Synapse observed new Alert: {target.id}")

    # We must use a separate background task to call async publish from a sync listener
    try:
        loop = asyncio.get_running_loop()
        # Fire and forget
        loop.create_task(event_bus.publish("alert.created", payload={
            "alert_id": str(target.id),
            "district_id": str(target.district_id),
            "disease": target.disease,
            "risk_score": float(target.risk_score),
            "alert_type": target.alert_type.value,
        }))
    except RuntimeError:
        # If no running event loop, this is a sync context (e.g., initial seed)
        pass

# Attach the SQLAlchemy listener
event.listen(Alert, 'after_insert', on_alert_created)


# 2. EventBus Subscriber to bridge EventBus -> User Notifications
async def handle_new_alert(payload: dict):
    """
    Listens to 'alert.created' and correlates it with User data.
    Finds officers assigned to the affected district whose alert_threshold is exceeded.
    """
    alert_id = payload.get("alert_id")
    district_id = payload.get("district_id")
    disease = payload.get("disease")
    risk_score = payload.get("risk_score")

    logger.info(f"Synapse correlating Alert {alert_id} with User data...")

    async with SessionLocal() as db:
        try:
            # Get the district name for the notification
            district = await db.scalar(select(District).where(District.id == district_id))
            district_name = district.name if district else "Unknown District"

            # Intelligence: Find users assigned to this district who care about this risk level
            # 1. Must be linked to the district via user_districts
            # 2. User's personal alert_threshold must be <= the alert's risk_score
            # 3. User must have email_alerts enabled

            # Note: risk_score is typically 0-1 or 0-100.
            # In prediction it's 0-100. In Alerts it might be 0-1.
            # Convert user threshold to a comparable decimal if necessary
            # Let's assume user.alert_threshold is 0-100 (default 70).
            # Let's ensure comparable scale. If risk is < 1, multiply by 100
            comparable_risk = risk_score * 100 if risk_score <= 1.0 else risk_score

            query = (
                select(User)
                .join(User.districts)
                .where(District.id == district_id)
                .where(User.is_active == True)
                .where(User.email_alerts == True)
                .where(User.alert_threshold <= comparable_risk)
            )

            result = await db.execute(query)
            affected_users = result.scalars().all()

            if affected_users:
                logger.info(f"Synapse found {len(affected_users)} users assigned to {district_name} exceeding threshold for alert {alert_id}.")
                # Notify users (Simulated via task)
                for user in affected_users:
                    logger.info(f"Synapse Dispatching to {user.email} (Threshold: {user.alert_threshold} <= Risk: {comparable_risk})")
                    asyncio.create_task(send_alert_notification(
                        alert_id=alert_id,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    ))
            else:
                logger.info(f"Synapse: No users found meeting notification criteria for alert {alert_id} in {district_name}.")

        except Exception as e:
            logger.error(f"Synapse failed to process alert {alert_id}: {str(e)}", exc_info=True)


# Register the subscriber
event_bus.subscribe("alert.created", handle_new_alert)
