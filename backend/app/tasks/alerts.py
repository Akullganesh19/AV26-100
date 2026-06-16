import logging
import time
from uuid import UUID
from app.core.database import SessionLocal
from app.services.intelligence_bridge import IntelligenceBridge

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, district_id: str | UUID | None = None):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score,
            "district_id": str(district_id) if district_id else None
        }
    )
    
    try:
        targeted_officers = []
        if district_id:
            # Intelligence Bridge: Fetch officers specifically monitoring this district
            # and whose threshold is exceeded by this risk score.
            async with SessionLocal() as db:
                targeted_officers = await IntelligenceBridge.get_targeted_officers(db, district_id, risk_score)

        if not targeted_officers and district_id:
            logger.info(f"No targeted officers met criteria for alert {alert_id}. Suppressing broadcast.")
            return {"status": "suppressed", "reason": "no_targeted_officers"}

        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        
        if targeted_officers:
            for officer in targeted_officers:
                logger.info(f"Dispatching targeted alert to {officer['email']} (Threshold: {officer['threshold']})")

        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id, "targeted_count": len(targeted_officers)}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
