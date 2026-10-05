import logging
import time
from uuid import UUID
from app.api.integrations import integration_service
from app.core.config import settings
from app.core.resilience import with_retry

logger = logging.getLogger(__name__)

@with_retry(max_attempts=3, base_delay=0.5)
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
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        # Real SendGrid logic with retry built into the integration service
        if getattr(settings, 'SENDGRID_API_KEY', None) and settings.SENDGRID_API_KEY != "dummy":
            await integration_service.send_health_alert_email(
                to_email="health.official@example.com", # In real life, fetch from DB
                district_name=district_name,
                disease=disease,
                risk_score=risk_score
            )
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        raise # Reraise to trigger @with_retry
