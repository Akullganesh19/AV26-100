import logging
import time
import asyncio
from uuid import UUID
from sqlalchemy import select, and_

from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.district import District

logger = logging.getLogger(__name__)

# Strong reference for background tasks
_background_tasks = set()

async def process_alert_triggered(event_data: dict):
    """Listener that queries Auth/Users system to route Alerts."""
    alert_id = event_data.get("alert_id")
    district_id = event_data.get("district_id")
    district_name = event_data.get("district_name", str(district_id))
    disease = event_data.get("disease")
    risk_score = event_data.get("risk_score")

    if not district_id:
        return

    try:
        async with SessionLocal() as db:
            # Find users watching this district with email_alerts enabled and threshold met
            query = select(User).where(
                and_(
                    User.districts.any(District.id == district_id),
                    User.email_alerts == True,
                    User.alert_threshold <= (risk_score * 100)
                )
            )
            result = await db.execute(query)
            users = result.scalars().all()

            for user in users:
                task = asyncio.create_task(
                    send_alert_notification(alert_id, district_name, disease, risk_score, target_email=user.email)
                )
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)

    except Exception as e:
        logger.error(f"Failed to route alert {alert_id} to users: {e}", exc_info=True)


def setup_subscribers():
    """Register event subscribers."""
    event_bus.subscribe("alert.triggered", process_alert_triggered)


async def send_alert_notification(alert_id: str, district_name: str, disease: str, risk_score: float, target_email: str = None):
    """
    Asynchronous task to deliver critical alerts to health officials.
    """
    logger.info(
        f"Initiating alert dispatch for {alert_id} to {target_email or 'all'}",
        extra={
            "district": district_name,
            "disease": disease,
            "risk_score": risk_score,
            "target_email": target_email
        }
    )
    
    try:
        # Simulate third-party integration (e.g., SendGrid/Twilio)
        # Using settings.SENDGRID_API_KEY
        msg = f"CRITICAL ALERT: Outbreak risk detected in {district_name} ({disease}). Score: {risk_score}"
        if target_email:
            msg = f"[To: {target_email}] {msg}"
        logger.info(msg)
        
        # Here you would implement real SendGrid logic
        # if settings.SENDGRID_API_KEY:
        #     ... 
        
        return {"status": "dispatched", "alert_id": alert_id, "target_email": target_email}
        
    except Exception as exc:
        logger.error(f"Dispatch failed for {alert_id}: {str(exc)}")
        return {"status": "failed", "error": str(exc)}
