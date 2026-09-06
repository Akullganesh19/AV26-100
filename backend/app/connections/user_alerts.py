import logging
import asyncio
from sqlalchemy import text
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

# Set to maintain strong references to background tasks
_notification_tasks = set()

async def on_alert_triggered(alert_id: str, district_id: str, disease: str, risk_score: float):
    logger.info(f"Connection Layer triggered for alert {alert_id} in {district_id} ({disease})")

    # Convert district_id to string, handle UUID format if needed
    district_id_str = str(district_id)

    async with SessionLocal() as db:
        # 1. Fetch district name
        district_query = text("SELECT name FROM districts WHERE id = :district_id")
        district_result = await db.execute(district_query, {"district_id": district_id_str})
        district_row = district_result.fetchone()
        district_name = district_row[0] if district_row else "Unknown District"

        # 2. Find eligible users in this district (personal alert_threshold <= risk_score * 100, and email_alerts=True)
        # We use risk_score * 100 because alert_threshold is 0-100, while risk_score is usually 0.0-1.0 from clinical, though autonomous might be 0-100.
        adjusted_score = risk_score * 100 if risk_score <= 1.0 else risk_score

        user_query = text("""
            SELECT u.id, u.name, u.email
            FROM users u
            JOIN user_districts ud ON u.id = ud.user_id
            WHERE ud.district_id = :district_id
              AND u.email_alerts = True
              AND u.alert_threshold <= :adjusted_score
        """)

        users_result = await db.execute(user_query, {
            "district_id": district_id_str,
            "adjusted_score": adjusted_score
        })
        users = users_result.fetchall()

        if not users:
            logger.info(f"No eligible users found for alert {alert_id}")
            return

        logger.info(f"Found {len(users)} eligible users for alert {alert_id}. Dispatching notifications...")

        # 3. Fan out notifications
        for user in users:
            logger.info(f"Routing alert {alert_id} to user {user.id} ({user.email})")
            task = asyncio.create_task(send_alert_notification(
                alert_id=str(alert_id),
                district_name=district_name,
                disease=disease,
                risk_score=float(risk_score)
            ))
            _notification_tasks.add(task)
            task.add_done_callback(_notification_tasks.discard)

# Register the listener
event_bus.on('alert.triggered', on_alert_triggered)
logger.info("Synapse Connection: Registered 'alert.triggered' listener in user_alerts")
