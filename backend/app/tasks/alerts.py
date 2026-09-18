import asyncio
import logging
import time
from typing import Optional
from uuid import UUID

from sqlalchemy import text

from app.core.database import SessionLocal
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

active_tasks = set()

async def correlate_and_notify_users(district_id: str, district_name: str, disease: str, risk_score: float):
    try:
        async with SessionLocal() as db:
            query = text("""
                SELECT u.email
                FROM users u
                JOIN user_districts ud ON u.id = ud.user_id
                WHERE ud.district_id = :dist_id
                  AND u.email_alerts = true
                  AND u.alert_threshold <= :risk
            """)
            result = await db.execute(query, {"dist_id": district_id, "risk": risk_score})
            emails = [row[0] for row in result.fetchall()]

            for email in emails:
                try:
                    await integration_service.send_health_alert_email(
                        to_email=email,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score
                    )
                    logger.info(f"Notified {email} for district {district_id}")
                except Exception as e:
                    logger.error(f"Failed to send email to {email}: {e}")
    except Exception as e:
        logger.error(f"Failed to correlate users for {district_id}: {e}")

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, district_id: Optional[str] = None):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    if district_id:
        task = asyncio.create_task(correlate_and_notify_users(district_id, district_name, disease, risk_score))
        active_tasks.add(task)
        task.add_done_callback(active_tasks.discard)

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
