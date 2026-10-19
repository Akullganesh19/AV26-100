import logging
import time
import json
from uuid import UUID
import redis.asyncio as redis
from app.core.config import settings
from app.core.resilience import with_retry

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
        from app.api.integrations import integration_service
        await with_retry(
            integration_service.send_health_alert_email,
            to_email=settings.EMAILS_FROM_EMAIL,
            district_name=district_name,
            disease=disease,
            risk_score=risk_score
        )
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch permanently failed for {alert_id}: {str(exc)}. Pushing to DLQ.")
        try:
            r = redis.from_url(str(settings.CELERY_BROKER_URL))
            payload = json.dumps({
                "alert_id": alert_id,
                "district_name": district_name,
                "disease": disease,
                "risk_score": risk_score,
                "error": str(exc)
            })
            await r.lpush("dead-letter", payload)
            await r.aclose()
        except Exception as dlq_exc:
            logger.critical(f"DLQ PUSH FAILED for {alert_id}: {dlq_exc}")
        return {"status": "failed", "error": str(exc)}
