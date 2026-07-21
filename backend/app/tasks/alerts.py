import logging
import time
from uuid import UUID
from sqlalchemy import select
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score
        }
    )
    
    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}

@event_bus.on('alert.triggered')
async def handle_alert_triggered(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Listener for when an alert is triggered. Maps the district to users and sends targeted notifications.
    """
    logger.info(f"Handling 'alert.triggered' event for alert {alert_id}, district {district_id}")

    try:
        async with SessionLocal() as db:
            # Query District Name for better logging
            district_result = await db.execute(select(District).where(District.id == district_id))
            district = district_result.scalar_one_or_none()
            district_name = district.name if district else str(district_id)

            # Send generic fallback notification with resolved name
            await send_alert_notification(alert_id, district_name, disease, risk_score)

            # Query Users mapped to this district with threshold met and email alerts enabled
            # Note: alert_threshold is stored as integer (e.g. 70 for 70%)
            query = (
                select(User)
                .join(User.districts)
                .where(District.id == district_id)
                .where(User.alert_threshold <= risk_score * 100)
                .where(User.email_alerts == True)
                .where(User.is_active == True)
            )
            result = await db.execute(query)
            target_users = result.scalars().all()

            for user in target_users:
                logger.info(
                    f"TARGETED ALERT: User {user.email} notified about {disease} in {district_name} "
                    f"(Score: {risk_score*100:.1f}%, User Threshold: {user.alert_threshold}%)"
                )
                # Here you would dispatch actual targeted email/SMS for the user

    except Exception as exc:
        logger.error(f"Failed to handle alert.triggered event for {alert_id}: {str(exc)}", exc_info=True)
