import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.models.alert import Alert
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification
from app.core.event_bus import event_bus

logger = logging.getLogger(__name__)

async def handle_alert_triggered(alert: Alert):
    """
    Listens for new alerts and routes targeted notifications to users
    who oversee the affected district and have their alert threshold met.
    """
    try:
        async with SessionLocal() as db:
            # Fetch users assigned to this district
            query = select(User).join(user_district_association).where(
                user_district_association.c.district_id == alert.district_id,
                User.email_alerts.is_(True)
            )
            result = await db.execute(query)
            users = result.scalars().all()

            # Also fetch district name
            district = await db.get(District, alert.district_id)
            district_name = district.name if district else str(alert.district_id)

            for user in users:
                # Check if risk score exceeds user's personalized threshold
                # risk_score is 0.0 - 1.0, user threshold is 0 - 100
                if (float(alert.risk_score) * 100) >= user.alert_threshold:
                    logger.info(f"Routing alert {alert.id} to {user.email}")
                    await send_alert_notification(
                        alert_id=str(alert.id),
                        district_name=district_name,
                        disease=alert.disease,
                        risk_score=float(alert.risk_score),
                        email=user.email
                    )
    except Exception as e:
        logger.error(f"Failed to route targeted notifications for alert {alert.id}: {e}", exc_info=True)

# Subscribe to the event
event_bus.subscribe("alert.triggered", handle_alert_triggered)
