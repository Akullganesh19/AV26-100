import logging
import time
from uuid import UUID
import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.user_district import user_district_association


logger = logging.getLogger(__name__)

_background_tasks = set()

def dispatch_targeted_alert(alert_id: str, district_id: str, district_name: str, disease: str, risk_score: float):
    task = asyncio.create_task(send_alert_notification(alert_id, district_id, district_name, disease, risk_score))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task

async def send_alert_notification(alert_id: str, district_id: str, district_name: str, disease: str, risk_score: float):
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
        
        normalized_score = risk_score * 100

        async with SessionLocal() as db:
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(
                    user_district_association.c.district_id == district_id,
                    User.email_alerts.is_(True),
                    User.alert_threshold <= normalized_score
                )
            )
            result = await db.execute(query)
            targeted_users = result.scalars().all()

            for user in targeted_users:
                logger.info(f"Dispatching targeted alert to {user.email} (threshold {user.alert_threshold} <= {normalized_score})")


        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
