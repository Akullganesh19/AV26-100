import logging
import time
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.api.integrations import integration_service
from app.core.events import event_bus

logger = logging.getLogger(__name__)

async def notify_stakeholders_on_alert(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Subscribes to alert.triggered event.
    Cross-system intelligence: Uses Auth system (User + District config) to precisely route alerts.
    """
    try:
        async with SessionLocal() as db:
            # Join users and districts via association table
            query = (
                select(User, District)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .join(District, District.id == user_district_association.c.district_id)
                .where(
                    District.id == district_id,
                    User.email_alerts == True,
                    (risk_score * 100) >= User.alert_threshold
                )
            )
            result = await db.execute(query)

            for user, district in result:
                logger.info(f"Routing alert for {disease} to user {user.email} (Threshold: {user.alert_threshold})")
                await integration_service.send_health_alert_email(
                    to_email=user.email,
                    district_name=district.name,
                    disease=disease,
                    risk_score=risk_score
                )
    except Exception as exc:
        logger.error(f"Failed to notify stakeholders for alert {alert_id}: {str(exc)}", exc_info=True)

# Register the event listener
event_bus.subscribe("alert.triggered", notify_stakeholders_on_alert)

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
