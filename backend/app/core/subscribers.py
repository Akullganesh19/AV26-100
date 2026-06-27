import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.events import bus
from app.core.database import SessionLocal
from app.models.alert import Alert, AlertType, AlertStatus
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def handle_alert_created(alert: Alert):
    if alert.status == AlertStatus.TRIGGERED:
        logger.info(f"Subscribers: processing created alert {alert.id} for district {alert.district_id}")

        async def process_notification():
            async with SessionLocal() as db:
                # Get the district name for the email
                district = await db.get(District, alert.district_id)
                district_name = district.name if district else str(alert.district_id)

                # We need to query for users who are associated with this district,
                # have email_alerts enabled, and their alert_threshold is <= the alert's risk_score.
                # Note: alert.risk_score might be a decimal between 0-1 or 0-100 depending on model.
                # Threshold is usually 0-100.
                alert_score_normalized = float(alert.risk_score)
                if alert_score_normalized <= 1.0:
                     alert_score_normalized *= 100.0

                query = (
                    select(User)
                    .join(User.districts)
                    .where(
                        and_(
                            District.id == alert.district_id,
                            User.email_alerts == True,
                            User.alert_threshold <= alert_score_normalized,
                            User.is_active == True
                        )
                    )
                )
                result = await db.execute(query)
                users = result.scalars().all()

                if not users:
                    logger.info(f"No active users met threshold criteria for alert {alert.id}")
                    return

                # Send notifications to users
                emails = [user.email for user in users]
                logger.info(f"Dispatching alert {alert.id} to {len(emails)} targeted users")

                await send_alert_notification(
                    alert_id=str(alert.id),
                    district_name=district_name,
                    disease=alert.disease,
                    risk_score=float(alert.risk_score),
                    recipient_emails=emails
                )

        # Fire and forget task to not block the current thread
        loop = asyncio.get_running_loop()
        loop.create_task(process_notification())

# Register the subscribers
bus.subscribe("alert.created", handle_alert_created)
