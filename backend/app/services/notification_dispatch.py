import logging
import asyncio
from typing import Dict, Any

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)


async def handle_alert_created(payload: Dict[str, Any]):
    """
    Subscribes to 'alert.created'.
    Finds users associated with the alert's district who want emails
    and have a threshold <= the alert's risk score.
    """
    district_id = payload.get("district_id")
    disease = payload.get("disease")
    risk_score = payload.get("risk_score")
    alert_id = payload.get("alert_id")

    if not all([district_id, disease, risk_score, alert_id]):
        logger.error(
            "Missing required payload fields for alert.created in handle_alert_created"
        )
        return

    try:
        async with SessionLocal() as db:
            # Query the User system:
            # Join with User.districts to get users for the specific district
            # Filter by email_alerts=True and alert_threshold <= risk_score * 100

            # Since User.districts is a many-to-many relationship, we query Users
            # that have this district in their districts list.
            query = (
                select(User)
                .join(User.districts)
                .where(District.id == district_id)
                .where(User.email_alerts.is_(True))
                .where(User.alert_threshold <= int(risk_score * 100))
            )

            result = await db.execute(query)
            affected_users = result.scalars().all()

            # Fetch district name for notification
            district_query = select(District).where(District.id == district_id)
            district_res = await db.execute(district_query)
            district = district_res.scalar_one_or_none()
            district_name = district.name if district else "Unknown District"

            logger.info(
                f"Notification dispatch: Found {len(affected_users)} users to notify for alert {alert_id}"
            )

            # Dispatch personalized notifications
            for user in affected_users:
                asyncio.create_task(
                    send_alert_notification(
                        alert_id=str(alert_id),
                        district_name=district_name,
                        disease=disease,
                        risk_score=float(risk_score),
                        user_email=user.email,
                        user_name=user.name,
                    )
                )

    except Exception as e:
        logger.error(f"Error in handle_alert_created dispatch: {e}", exc_info=True)


def setup_dispatch_listeners():
    """Register all listeners for the notification dispatch layer."""
    event_bus.subscribe("alert.created", handle_alert_created)
    logger.info("Synapse Notification Dispatch initialized")
