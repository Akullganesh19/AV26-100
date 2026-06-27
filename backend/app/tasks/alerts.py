import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

async def send_alert_notification(
    alert_id: str,
    district_name: str,
    disease: str,
    risk_score: float,
    recipient_emails: Optional[List[str]] = None
):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score,
            "recipients_count": len(recipient_emails) if recipient_emails else 0
        }
    )
    
    try:
        if not recipient_emails:
            logger.warning(f"No recipient emails provided for alert {alert_id}. Notification skipped.")
            return {"status": "skipped", "reason": "no_recipients"}

        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        logger.info(f"Sending emails to: {', '.join(recipient_emails)}")
        
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id, "recipients_count": len(recipient_emails)}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
