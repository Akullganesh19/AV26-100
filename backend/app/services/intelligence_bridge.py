import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification
from app.core.events import event_bus

logger = logging.getLogger(__name__)

async def handle_high_risk_prediction(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Subscribes to 'prediction.high_risk' and bridges the Auth system (Users/Preferences)
    with the Prediction/Alerts system, delivering personalized intelligence.
    """
    async with SessionLocal() as db:
        # Fetch district with users to evaluate preferences
        result = await db.execute(
            select(District).options(selectinload(District.users)).where(District.id == district_id)
        )
        district = result.scalar_one_or_none()

        if not district:
            logger.warning(f"IntelligenceBridge: District {district_id} not found.")
            return

        for user in district.users:
            if user.email_alerts and (risk_score * 100) >= user.alert_threshold:
                logger.info(
                    f"IntelligenceBridge: Risk {risk_score} in {district.name} exceeds {user.name}'s threshold {user.alert_threshold}."
                )
                await send_alert_notification(
                    alert_id=alert_id,
                    district_name=district.name,
                    disease=disease,
                    risk_score=risk_score,
                    target_email=user.email
                )

def setup_intelligence_connections():
    event_bus.subscribe("prediction.high_risk", handle_high_risk_prediction)
    logger.info("Synapse Intelligence Bridge established.")
