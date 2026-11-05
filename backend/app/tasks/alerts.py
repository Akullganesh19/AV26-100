import logging
import time
from uuid import UUID
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_id: UUID, disease: str, risk_score: float):
    """
    Asynchronous task to deliver critical alerts to health officials.
    Enriches alert with user data to selectively notify assigned officers.
    """
    notified_officers = []
    district_name = "Unknown District"

    try:
        async with SessionLocal() as db:
            # Get district name
            district_query = select(District.name).where(District.id == district_id)
            district_result = await db.execute(district_query)
            district_name = district_result.scalar_one_or_none() or "Unknown District"

            # Cross-system intelligence: User Auth ↔ Alerts
            # Only notify officers assigned to this district, with alerts enabled, whose threshold is met
            user_query = (
                select(User.email)
                .join(User.districts)
                .where(District.id == district_id)
                .where(User.email_alerts == True)
                .where(User.alert_threshold <= risk_score * 100)
            )
            user_result = await db.execute(user_query)
            notified_officers = user_result.scalars().all()

        logger.info(
            f"Initiating alert dispatch for {alert_id}",
            extra={
                "district": district_name,
                "disease": disease,
                "risk_score": risk_score,
                "notified_officers": notified_officers
            }
        )

        if not notified_officers:
            logger.info(f"No officers met criteria for alert {alert_id} in {district_name}")
            return {"status": "skipped", "alert_id": alert_id, "reason": "No officers matched criteria"}

        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}. Notifying: {notified_officers}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id, "notified_count": len(notified_officers)}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
