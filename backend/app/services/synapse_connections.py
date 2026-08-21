import logging
from typing import Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_interested_users(alert_data: Dict[str, Any]):
    """
    Listener for 'alert.triggered'.
    Finds users who track the district and have an alert threshold <= risk score.
    """
    logger.info(f"Synapse routing alert for district {alert_data.get('district_id')}")
    try:
        async with SessionLocal() as db:
            district_id = alert_data.get("district_id")
            disease = alert_data.get("disease")
            risk_score = float(alert_data.get("risk_score", 0))
            alert_id = alert_data.get("alert_id")

            # Multiply risk_score by 100 to match user's threshold scale (0-100)
            scaled_risk = risk_score * 100

            # Find users tracking this district via the association table
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(
                    and_(
                        user_district_association.c.district_id == district_id,
                        User.email_alerts == True,
                        User.alert_threshold <= scaled_risk
                    )
                )
            )

            result = await db.execute(query)
            users = result.scalars().all()

            if users:
                logger.info(f"Synapse identified {len(users)} users for alert {alert_id}")
                for user in users:
                    # Enrich the generic notification with user context
                    await send_alert_notification(
                        alert_id=str(alert_id),
                        district_name=str(district_id), # Mock district name as ID for this scope
                        disease=disease,
                        risk_score=risk_score,
                        user_email=user.email
                    )
            else:
                logger.info(f"Synapse: No interested users for alert {alert_id}")

    except Exception as e:
        logger.error(f"Synapse connection failed: {e}", exc_info=True)

def init_synapse_connections():
    """Wire up the loose connections."""
    event_bus.on("alert.triggered", route_alert_to_interested_users)
    logger.info("Synapse pathways initialized")
