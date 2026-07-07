import logging
import time
from uuid import UUID

logger = logging.getLogger(__name__)

from app.api.integrations import integration_service
from app.core.config import settings

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, user_email: str):
    """
    Asynchronous task to deliver targeted critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id} to {user_email}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score,
            "user_email": user_email
        }
    )
    
    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT TO {user_email}: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        if settings.SENDGRID_API_KEY:
            await integration_service.send_health_alert_email(
                to_email=user_email,
                district_name=district_name,
                disease=disease,
                risk_score=risk_score
            )
        
        return {"status": "dispatched", "alert_id": alert_id, "user_email": user_email}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
