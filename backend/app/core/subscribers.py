import logging
import asyncio
from typing import Dict, Any

from app.core.events import event_bus
from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def handle_alert_triggered(payload: Dict[str, Any]):
    """
    Subscribes to 'alert.triggered' and finds users interested in this alert.
    Payload expected:
    {
        "alert_id": str,
        "district_id": str,
        "disease": str,
        "risk_score": float
    }
    """
    alert_id = payload.get("alert_id")
    district_id = payload.get("district_id")
    disease = payload.get("disease")
    risk_score = payload.get("risk_score", 0.0)

    try:
        async with SessionLocal() as db:
            query = (
                select(User, District.name)
                .join(User.districts)
                .where(
                    District.id == district_id,
                    User.email_alerts == True,
                    User.alert_threshold <= risk_score
                )
            )
            result = await db.execute(query)

            if not hasattr(handle_alert_triggered, '_tasks'):
                handle_alert_triggered._tasks = set()

            for row in result.all():
                user, district_name = row
                # Dispatch targeted notification
                task = asyncio.create_task(
                    send_alert_notification(
                        alert_id=alert_id,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
                )
                # Keep strong reference
                handle_alert_triggered._tasks.add(task)
                task.add_done_callback(handle_alert_triggered._tasks.discard)

    except Exception as e:
        logger.error(f"Error handling 'alert.triggered' event: {e}", exc_info=True)

event_bus.subscribe("alert.triggered", handle_alert_triggered)
