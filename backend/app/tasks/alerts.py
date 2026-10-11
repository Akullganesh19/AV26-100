import logging
import time
from uuid import UUID
from app.core.events import event_bus
from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.user import User
from app.models.district import District

logger = logging.getLogger(__name__)

async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, user_email: str):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id} to {user_email}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score,
            "user_email": user_email
        }
    )
    
    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        logger.info(f"CRITICAL ALERT TO {user_email}: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}")
        return {"status": "dispatched", "alert_id": alert_id}
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id} to {user_email}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}

async def notify_users_of_high_risk(prediction_data: dict):
    """Subscriber for prediction.high_risk events."""
    alert_id = prediction_data.get("alert_id")
    district_id = prediction_data.get("district_id")
    disease = prediction_data.get("disease")
    risk_score = prediction_data.get("risk_score")

    try:
        async with SessionLocal() as db:
            district_res = await db.execute(select(District).where(District.id == district_id))
            district = district_res.scalar_one_or_none()
            district_name = district.name if district else "Unknown District"

            users_res = await db.execute(
                select(User)
                .join(User.districts)
                .where(District.id == district_id)
            )
            users = users_res.scalars().all()

            for user in users:
                if user.email_alerts and (risk_score * 100) >= user.alert_threshold:
                    await send_alert_notification(
                        alert_id=alert_id,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
    except Exception as e:
        logger.error(f"Failed to notify users of high risk: {e}", exc_info=True)

def setup_subscribers():
    event_bus.subscribe("prediction.high_risk", notify_users_of_high_risk)
