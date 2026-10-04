import logging
import asyncio
from sqlalchemy import select, text
from app.events import event_bus
from app.models.alert import Alert
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.core.database import SessionLocal
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(alert: Alert):
    """
    Listens for new tactical alerts and routes them to users assigned to the
    affected district who have email_alerts enabled and a matching risk threshold.
    """
    logger.info(f"Synapse: Evaluating routing for Alert {alert.id}")

    async with SessionLocal() as db:
        # Load the district name
        district_result = await db.execute(select(District).where(District.id == alert.district_id))
        district = district_result.scalar_one_or_none()
        district_name = district.name if district else "Unknown District"

        # Find users who monitor this district and want alerts
        query = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(user_district_association.c.district_id == alert.district_id)
            .where(User.email_alerts == True)
            .where(User.is_active == True)
        )
        result = await db.execute(query)
        users = result.scalars().all()

        notified_count = 0
        for user in users:
            # Check user threshold against alert risk_score
            # risk_score is typically 0-1, alert_threshold is 0-100
            if (alert.risk_score * 100) >= user.alert_threshold:
                # Dispatch targeted notification
                task = asyncio.create_task(
                    send_alert_notification(
                        alert_id=str(alert.id),
                        district_name=district_name,
                        disease=alert.disease,
                        risk_score=float(alert.risk_score)
                    )
                )
                from app.connections import _background_tasks
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)
                notified_count += 1

        logger.info(f"Synapse: Alert {alert.id} routed to {notified_count} users")

# Register the listener
event_bus.on('alert.triggered', route_alert_to_users)
