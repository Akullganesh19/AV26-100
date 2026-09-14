import logging
import time
from uuid import UUID

logger = logging.getLogger(__name__)

import asyncio
from sqlalchemy import text
from app.core.database import SessionLocal
from app.api.integrations import integration_service

async def dispatch_district_alert_emails(alert_id: str, district_id: str, district_name: str, disease: str, risk_score: float):
    """
    Find users assigned to this district who have email_alerts enabled
    and alert_threshold <= risk_score, and send them email notifications.
    """
    logger.info(f"Dispatching emails for alert {alert_id} in district {district_id}")
    try:
        async with SessionLocal() as db:
            query = text('''
                SELECT u.email, u.name
                FROM users u
                JOIN user_districts ud ON u.id = ud.user_id
                WHERE ud.district_id = :district_id
                  AND u.email_alerts = true
                  AND u.alert_threshold <= :risk_score
            ''')
            result = await db.execute(query, {"district_id": district_id, "risk_score": risk_score * 100})
            users = result.all()

            for user in users:
                logger.info(f"Sending alert email to {user.email}")
                await integration_service.send_health_alert_email(
                    to_email=user.email,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
    except Exception as exc:
        logger.error(f"Failed to dispatch emails for alert {alert_id}: {str(exc)}", exc_info=True)


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
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
