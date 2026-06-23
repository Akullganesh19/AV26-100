import logging
import asyncio
from app.core.events import event_bus
from app.models.alert import Alert
from app.models.user import User
from app.models.district import District
from app.core.database import SessionLocal
from sqlalchemy import select
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_users(alert: Alert):
    """
    Synapse intelligence: When a new alert is generated, find all users
    who have opted in for alerts in that jurisdiction and whose risk
    threshold is met. Dispatch targeted notifications to them.
    """
    logger.info(f"Synapse: Processing new alert {alert.id} for district {alert.district_id}")

    async with SessionLocal() as db:
        # We need the district name for the notification
        district_result = await db.execute(select(District).where(District.id == alert.district_id))
        district = district_result.scalar_one_or_none()
        district_name = district.name if district else str(alert.district_id)

        # Join User -> user_districts to find interested parties
        stmt = (
            select(User)
            .where(
                User.districts.any(id=alert.district_id),
                User.email_alerts == True,
                User.alert_threshold <= float(alert.risk_score * 100)
            )
        )

        result = await db.execute(stmt)
        users = result.scalars().all()

        for user in users:
            logger.info(f"Synapse: Routing alert {alert.id} to user {user.email} (threshold {user.alert_threshold} <= {float(alert.risk_score * 100)})")
            # In a real system, we'd enqueue a celery task here.
            # We'll use the existing send_alert_notification helper.
            # But we wrap it in a task since send_alert_notification might be slow.
            asyncio.create_task(
                send_alert_notification(
                    alert_id=str(alert.id),
                    district_name=district_name,
                    disease=alert.disease,
                    risk_score=float(alert.risk_score)
                )
            )

# Subscribe to the EventBus
event_bus.subscribe("alert.created", route_alert_to_users)
