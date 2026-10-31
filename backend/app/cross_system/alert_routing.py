import logging
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionLocal
from app.models.district import District
from app.tasks.alerts import send_alert_notification
from app.cross_system.event_bus import event_bus

logger = logging.getLogger(__name__)

async def route_high_risk_prediction(district_id: str, disease: str, risk_score: float, prediction_id: str):
    """
    Intelligently route a high-risk prediction to users who care about it.
    Connects the Analytics/Prediction domain to the Auth/User domain.
    """
    async with SessionLocal() as db:
        # Get district and eagerly load its users
        query = select(District).options(selectinload(District.users)).where(District.id == district_id)
        result = await db.execute(query)
        district = result.scalar_one_or_none()

        if not district:
            logger.error(f"District {district_id} not found when routing alert.")
            return

        affected_users = []
        for user in district.users:
            # Check user thresholds and preferences
            if user.is_active and user.email_alerts and (risk_score * 100) >= user.alert_threshold:
                affected_users.append(user)

        logger.info(f"Routing prediction {prediction_id} to {len(affected_users)} users based on custom thresholds.")

        # Dispatch notifications
        if affected_users:
            for user in affected_users:
                 asyncio.create_task(send_alert_notification(
                    alert_id=prediction_id,
                    district_name=district.name,
                    disease=disease,
                    risk_score=risk_score,
                    user_email=user.email,
                    user_id=str(user.id)
                ))
        else:
             # Maintain default behavior for backwards compatibility
             asyncio.create_task(send_alert_notification(
                alert_id=prediction_id,
                district_name="Jurisdiction Monitor",
                disease=disease,
                risk_score=risk_score
            ))

# Connect the systems
event_bus.subscribe("prediction.high_risk", route_high_risk_prediction)
