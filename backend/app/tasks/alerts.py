import logging
import time
from uuid import UUID

logger = logging.getLogger(__name__)

from app.core.database import SessionLocal
from sqlalchemy import text

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, district_id: str = None):
    """
    Asynchronous task to deliver critical alerts to health officials.
    Routes alerts dynamically based on user preferences and assignments.
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
        # Cross-System Intelligence: Connect Auth (Users) with Alerts
        target_users = []
        if district_id:
            async with SessionLocal() as db:
                query = text("""
                    SELECT u.email
                    FROM users u
                    JOIN user_districts ud ON u.id = ud.user_id
                    WHERE ud.district_id = :district_id
                      AND u.email_alerts = True
                      AND u.alert_threshold <= :adjusted_risk_score
                """)
                result = await db.execute(query, {
                    "district_id": district_id,
                    "adjusted_risk_score": risk_score * 100
                })
                target_users = [row[0] for row in result.fetchall()]
                logger.info(f"Alert routed to {len(target_users)} officials for district {district_id}")

        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}. Targets: {target_users}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
