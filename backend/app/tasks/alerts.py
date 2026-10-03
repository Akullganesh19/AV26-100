import logging
import time
import asyncio
from uuid import UUID

logger = logging.getLogger(__name__)

async def with_retry(func, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except Exception as err:
            if attempt == max_attempts:
                raise err
            await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

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
    
    async def _dispatch():
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    try:
        return await with_retry(_dispatch)
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
