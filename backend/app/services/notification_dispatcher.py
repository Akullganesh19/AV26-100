import logging
from sqlalchemy import select
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

@event_bus.on("alert.triggered")
async def handle_alert_triggered(alert_id: str, district_id: str, district_name: str, disease: str, risk_score: float):
    """
    Listens for 'alert.triggered' and routes notifications to users
    associated with the affected district who meet the threshold criteria.
    """
    logger.info(f"Notification dispatcher caught alert.triggered event for {alert_id}")

    # Needs a new DB session since this runs as an isolated background task
    async with SessionLocal() as db:
        try:
            # Query users associated with this district
            stmt = select(User).join(
                user_district_association,
                User.id == user_district_association.c.user_id
            ).where(
                user_district_association.c.district_id == district_id,
                User.is_active == True,
                User.email_alerts == True
            )

            result = await db.execute(stmt)
            users = result.scalars().all()

            notified_count = 0
            # Route to users whose threshold is met by the alert
            for user in users:
                if (risk_score * 100) >= user.alert_threshold:
                    logger.info(
                        f"Routing alert {alert_id} to user {user.id} ({user.email}). "
                        f"Alert Score: {risk_score * 100:.2f}, Threshold: {user.alert_threshold}"
                    )

                    # Dispatch the actual notification for this specific user
                    await send_alert_notification(
                        alert_id=alert_id,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
                    notified_count += 1

            logger.info(f"Alert {alert_id} routed to {notified_count} targeted users.")

        except Exception as e:
            logger.error(f"Error handling alert.triggered event for {alert_id}: {e}", exc_info=True)
