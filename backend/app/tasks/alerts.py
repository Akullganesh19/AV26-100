import logging
import time
from uuid import UUID
from app.api.integrations import integration_service

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
        
        # Real SendGrid Integration with built-in resilience
        await integration_service.send_health_alert_email(
            to_email="health@episense.org",
            district_name=district_name,
            disease=disease,
            risk_score=risk_score,
            idempotency_key=str(alert_id)
        )
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
