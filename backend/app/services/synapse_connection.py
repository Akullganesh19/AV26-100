import logging
from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.events import event_bus

logger = logging.getLogger("synapse.bridge")

async def route_alert_to_users(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Synapse Connection: Alerts <-> Users
    Subscribes to 'alert.triggered' and routes it to users interested in the district.
    """
    logger.info(f"Synapse Bridge: Alert {alert_id} fired. Querying affected users...")

    async with SessionLocal() as db:
        # Loose coupling: query user preferences via raw SQL, no imports of User/District models
        query = text("""
            SELECT u.id, u.email, u.name, u.alert_threshold, d.name as district_name
            FROM users u
            JOIN user_districts ud ON u.id = ud.user_id
            JOIN districts d ON d.id = ud.district_id
            WHERE ud.district_id = :district_id
              AND u.email_alerts = true
              AND u.is_active = true
        """)

        result = await db.execute(query, {"district_id": district_id})
        users = result.fetchall()

        notified_count = 0
        for user in users:
            # Normalize scores for comparison
            # If risk_score is 0-1 (clinical), threshold is 0-100
            # If risk_score is 0-100 (autonomous), threshold is 0-100
            score_normalized = risk_score * 100 if risk_score <= 1.0 else risk_score

            if score_normalized >= user.alert_threshold:
                logger.info(
                    f"Synapse Bridge: Routing alert {alert_id} ({disease} in {user.district_name}) "
                    f"to {user.name} <{user.email}> (Score: {score_normalized:.1f} >= Threshold: {user.alert_threshold})"
                )
                notified_count += 1

        logger.info(f"Synapse Bridge: Completed routing for alert {alert_id}. Notified {notified_count} users.")


def setup_synapse_connections():
    """Initializes cross-system event subscriptions."""
    event_bus.subscribe("alert.triggered", route_alert_to_users)
    logger.info("Synapse Bridge: Subscribed to alert.triggered events.")
