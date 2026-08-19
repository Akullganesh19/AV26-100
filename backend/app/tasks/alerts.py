import logging
import time
from uuid import UUID
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, district_id: UUID = None):
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
        
        # 🧠 SYNAPSE CONNECTION: Auth ↔ Alerts
        # Enrich the generic alert with targeted user context from the Auth system.
        if district_id:
            try:
                async with SessionLocal() as db:
                    query = select(User).join(User.districts).where(
                        District.id == district_id,
                        User.email_alerts == True,
                        User.alert_threshold <= (risk_score * 100)
                    )
                    result = await db.execute(query)
                    targeted_users = result.scalars().all()

                    if targeted_users:
                        emails = [u.email for u in targeted_users]
                        logger.info(f"SYNAPSE: Routing targeted alerts to {len(targeted_users)} officials: {emails}")
                    else:
                        logger.info("SYNAPSE: No officials met the threshold for this alert.")
            except Exception as e:
                logger.error(f"SYNAPSE: Failed to enrich alert with user context: {e}")

        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
