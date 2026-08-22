import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.district import District
from app.models.user import User
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Synapse Connection: Alerts ↔ Users
    Matches new alerts to users based on their district assignments and alert thresholds.
    """
    logger.info(f"🧠 Synapse: Routing alert {alert_id} for district {district_id} (score {risk_score})")

    async with SessionLocal() as db:
        # Load the district to get its name
        district_query = select(District).where(District.id == district_id)
        district_result = await db.execute(district_query)
        district = district_result.scalar_one_or_none()

        if not district:
            logger.warning(f"District {district_id} not found during alert routing")
            return

        district_name = district.name

        # Load all active users who are assigned to this district and have email alerts enabled
        users_query = select(User).options(selectinload(User.districts)).where(
            User.is_active == True,
            User.email_alerts == True
        )
        users_result = await db.execute(users_query)
        users = users_result.scalars().all()

        notified_count = 0
        for user in users:
            # Check if user monitors this district
            if any(str(d.id) == str(district_id) for d in user.districts):
                # Check user's personalized threshold (convert risk_score float to 0-100 scale)
                alert_threshold = float(user.alert_threshold)
                if (risk_score * 100) >= alert_threshold:
                    logger.info(f"🧠 Synapse: Notifying user {user.email} (threshold {alert_threshold} <= score {risk_score * 100})")
                    # Send alert - this integrates with the existing notification system
                    # Added email to log to indicate routing to specific user
                    # In a real system, send_alert_notification would take a user_email param
                    logger.info(f"Targeting user: {user.email}")
                    await send_alert_notification(
                        alert_id=str(alert_id),
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
                    notified_count += 1

        logger.info(f"🧠 Synapse: Alert {alert_id} routed to {notified_count} users")

def setup_intelligence():
    """Register all Synapse connections"""
    logger.info("🧠 Synapse: Initializing neural pathways")
    event_bus.subscribe("alert.triggered", route_alert_to_users)
