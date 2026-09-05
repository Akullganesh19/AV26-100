import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def route_alert_to_officers(db: AsyncSession, district_id: str, disease: str, risk_score: float, alert_id: str):
    """
    🧠 Synapse Connection: Alerts ↔ Users
    Routes alerts only to users who:
    1. Are assigned to the affected district.
    2. Have email alerts enabled.
    3. Have an alert threshold <= the risk score.

    Uses raw SQL to maintain loose coupling between Alert and User systems.
    """
    logger.info(f"SYNAPSE: Routing alert {alert_id} for {disease} in district {district_id}...")

    scaled_risk_score = risk_score * 100 if risk_score <= 1.0 else risk_score

    query = text("""
        SELECT u.id, u.name, u.email, u.alert_threshold
        FROM users u
        JOIN user_districts ud ON u.id = ud.user_id
        WHERE ud.district_id = :district_id
          AND u.email_alerts = True
          AND u.alert_threshold <= :scaled_risk_score
    """)

    result = await db.execute(query, {
        "district_id": district_id,
        "scaled_risk_score": scaled_risk_score
    })

    notified_users = []
    for row in result.fetchall():
        user_id, name, email, threshold = row
        logger.info(f"SYNAPSE: 🎯 Routing alert {alert_id} to {name} ({email}) - Threshold {threshold} <= {scaled_risk_score}")
        notified_users.append({
            "user_id": str(user_id),
            "email": email,
            "name": name
        })

    if not notified_users:
        logger.info(f"SYNAPSE: No officers found matching criteria for district {district_id} alert {alert_id}.")

    return notified_users
