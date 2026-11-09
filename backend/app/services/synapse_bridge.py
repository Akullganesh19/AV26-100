import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

background_tasks = set()

async def dispatch_targeted_alerts(district_id: str, alert_id: str, disease: str, risk_score: float):
    """
    🧠 SYNAPSE CONNECTION: Alert System ↔ Auth System ↔ Notification System

    Data flow:
    Alert is triggered -> Bridge queries Auth System for users associated with the district
    -> Bridge filters users by their personal alert_threshold -> Bridge dispatches Notifications.

    Coupling: Alert system just calls this bridge. Bridge relies on existing models.
    """
    try:
        normalized_risk = risk_score * 100 if risk_score <= 1.0 else float(risk_score)

        async with SessionLocal() as db:
            district_query = select(District.name).where(District.id == district_id)
            district_result = await db.execute(district_query)
            district_name = district_result.scalar_one_or_none() or "Unknown District"

            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(user_district_association.c.district_id == district_id)
                .where(User.email_alerts == True)
                .where(User.alert_threshold <= normalized_risk)
            )

            result = await db.execute(query)
            users_to_notify = result.scalars().all()

            if not users_to_notify:
                logger.info(f"🧠 SYNAPSE: No users met criteria for alert {alert_id} in {district_name}")
                return

        for user in users_to_notify:
            logger.info(f"🧠 SYNAPSE: Routing alert {alert_id} to user {user.email} (threshold {user.alert_threshold} <= {normalized_risk:.1f})")
            task = asyncio.create_task(
                send_alert_notification(
                    alert_id=str(alert_id),
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score,
                    user_email=user.email
                )
            )
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

    except Exception as e:
        logger.error(f"Synapse connection failed during alert dispatch: {e}")
