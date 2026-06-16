import logging
import time
from uuid import UUID
from app.core.config import settings
from app.api.integrations import integration_service
from app.core.resilience import with_retry, with_dead_letter_queue

logger = logging.getLogger(__name__)

@with_dead_letter_queue(queue_name="dead-letter")
@with_retry(max_retries=3, base_delay=0.1)
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
    
    # Send email through integration service (which also has circuit breaker built-in)
    logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")

    if settings.SENDGRID_API_KEY:
        # Replace hardcoded recipient with actual health command addresses
        recipient = settings.EMAILS_FROM_EMAIL
        await integration_service.send_health_alert_email(
            to_email=recipient,
            district_name=district_name,
            disease=disease,
            risk_score=risk_score
        )

    return {"status": "dispatched", "alert_id": alert_id}
