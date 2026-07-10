import logging
import time
from uuid import UUID

logger = logging.getLogger(__name__)

from celery import shared_task
from app.worker import celery_app
from app.core.config import settings

@celery_app.task(bind=True, max_retries=3)
def send_alert_notification_task(self, alert_id: str, district_name: str, disease: str, risk_score: float):
    """
    Celery task to deliver critical alerts to health officials.
    """
    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            logger.error(f"Dispatch permanently failed for {alert_id} after {self.max_retries} retries: {str(exc)}")
            # Dead Letter Queue Fallback using Celery Native Routing
            celery_app.send_task(
                "app.tasks.alerts.dlq_fallback",
                args=[alert_id, district_name, disease, risk_score],
                queue="dead-letter"
            )
            return {"status": "failed", "error": "Dispatch failed after retries"}

        # Exponential backoff: 2s, 4s, 8s
        backoff = 2 ** self.request.retries
        logger.warning(f"Transient dispatch failure for {alert_id}, retrying in {backoff}s. Error: {str(exc)}")
        raise self.retry(exc=exc, countdown=backoff)

@celery_app.task
def dlq_fallback(alert_id: str, district_name: str, disease: str, risk_score: float):
    logger.error(f"Alert {alert_id} captured by DLQ task")
    return {"status": "dlq", "alert_id": alert_id}

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float):
    """
    Asynchronous wrapper to queue the Celery task.
    Maintains compatibility with existing async codebase while delegating
    to robust Celery retry and DLQ logic.
    """
    logger.info(
        f"Queuing alert dispatch for {alert_id}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score
        }
    )
    send_alert_notification_task.delay(alert_id, district_name, disease, risk_score)
    return {"status": "queued", "alert_id": alert_id}
