import logging
import time
from uuid import UUID
from app.core.database import SessionLocal
from app.services.alert_routing import route_alert_to_officers

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id}",
        extra={
            "district_id": district_id,
            "disease": disease,
            "risk_score": risk_score
        }
    )
    
    try:
        # 🧠 Synapse Connection: Target only officers responsible for this district
        # whose alert threshold has been exceeded.
        async with SessionLocal() as db:
            officers = await route_alert_to_officers(db, district_id, disease, risk_score, alert_id)

        if not officers:
            logger.info(f"No officers targeted for alert {alert_id} in {district_id} (thresholds not met)")
            return {"status": "dispatched_none", "alert_id": alert_id}

        for officer in officers:
            logger.info(f"CRITICAL ALERT: Outbreak risk detected ({disease}). Sending to {officer['name']} ({officer['email']}) for district {district_id}. Score: {risk_score}")
            # Here you would implement real SendGrid logic per officer
            # if settings.SENDGRID_API_KEY:
            #     ...
        
        return {"status": "dispatched", "alert_id": alert_id, "officers_notified": len(officers)}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
