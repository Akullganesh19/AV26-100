import logging
import time
from uuid import UUID
from sqlalchemy import text
from app.core.database import SessionLocal

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
        # Retrieve target users using raw SQL for loose coupling (Synapse pattern)
        async with SessionLocal() as db:
            query = text('''
                SELECT u.id, u.email, u.name
                FROM users u
                JOIN user_districts ud ON u.id = ud.user_id
                JOIN districts d ON ud.district_id = d.id
                WHERE d.name = :district_name
                  AND u.email_alerts = True
                  AND u.alert_threshold <= :risk_score_pct
            ''')
            result = await db.execute(query, {
                "district_name": district_name,
                "risk_score_pct": int(risk_score * 100)
            })
            target_users = result.fetchall()

        recipients = [user.email for user in target_users]

        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        logger.info(f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}. Notifying {len(recipients)} targeted officers: {recipients}")
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id, "recipients": recipients}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
