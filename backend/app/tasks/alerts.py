import logging
import time
from uuid import UUID

logger = logging.getLogger(__name__)

from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.user import User

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, district_id: str = None):
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
        target_emails = []
        if district_id:
            async with SessionLocal() as db:
                # Check if risk score exceeds threshold. Usually thresholds are 0-100 or 0-1.
                # We will compare against user.alert_threshold.
                # Risk score might be already scaled to 100 since ALERT_THRESHOLD_DEFAULT=70.
                score_for_comparison = risk_score * 100 if risk_score <= 1.0 else risk_score

                # Note: using select() on users joined with districts.
                # We must use User.districts.any(id=district_id) based on the memory
                query = select(User).where(
                    User.districts.any(id=district_id),
                    User.email_alerts == True,
                    User.alert_threshold <= score_for_comparison
                )
                result = await db.execute(query)
                users = result.scalars().all()
                target_emails = [u.email for u in users]

        if target_emails:
            logger.info(f"Alert {alert_id} dynamically routed to users: {target_emails}")
        else:
            logger.info(f"Alert {alert_id}: No users matched routing criteria for {district_name}")

        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id, "routed_to": target_emails}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
