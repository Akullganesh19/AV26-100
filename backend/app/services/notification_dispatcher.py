import logging
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.district import District

logger = logging.getLogger(__name__)

async def handle_alert_triggered(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Listens for 'alert.triggered' events.
    Finds users associated with the district who meet the criteria to be notified.
    """
    async with SessionLocal() as db:
        try:
            # Query users mapped to the district, having email_alerts enabled,
            # and an alert_threshold less than or equal to the risk_score (scaled to 100).
            # Convert risk_score to 0-100 scale to compare with user alert_threshold
            normalized_score = risk_score * 100 if risk_score <= 1.0 else risk_score

            stmt = (
                select(User)
                .join(User.districts)
                .where(
                    and_(
                        District.id == district_id,
                        User.email_alerts == True,
                        User.alert_threshold <= normalized_score,
                        User.is_active == True
                    )
                )
            )
            result = await db.execute(stmt)
            users = result.scalars().all()

            if not users:
                logger.info(f"Targeted Notification: No subscribed users found for district {district_id} exceeding threshold {normalized_score}")
                return

            # In a real system we'd send an email here.
            # We log the specific, targeted intelligence gathered from the connection.
            for user in users:
                # Mask email to avoid leaking PII as per memory rules
                parts = user.email.split("@")
                masked_email = f"{parts[0][0]}***@{parts[1]}" if len(parts) == 2 else "***"
                logger.info(
                    f"TARGETED ALERT: Sending direct notification to {masked_email}",
                    extra={
                        "user_id": str(user.id),
                        "alert_id": alert_id,
                        "district_id": str(district_id),
                        "disease": disease,
                        "risk_score": float(risk_score),
                        "user_threshold": user.alert_threshold,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to process targeted notifications for alert {alert_id}: {str(e)}", exc_info=True)

# Register the listener
event_bus.on("alert.triggered", handle_alert_triggered)
