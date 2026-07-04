import logging
from sqlalchemy import select
from app.core.events import bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def handle_high_risk_prediction(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Subscribes to 'prediction.high_risk' and bridges the Auth/User system
    with the Notification/Alert system.
    Queries users who monitor the affected district and exceeds their alert threshold.
    """
    logger.info(f"Event received: prediction.high_risk for district {district_id}, risk={risk_score}")

    async with SessionLocal() as db:
        # Find district name
        dist_res = await db.execute(select(District).where(District.id == district_id))
        district = dist_res.scalar_one_or_none()
        district_name = district.name if district else str(district_id)

        # Find affected users: subscribed to district, active, email_alerts on, threshold met
        query = (
            select(User)
            .join(User.districts)
            .where(District.id == district_id)
            .where(User.is_active == True)
            .where(User.email_alerts == True)
            .where(User.alert_threshold <= (risk_score * 100)) # Risk score is 0-1, threshold is 0-100
        )

        result = await db.execute(query)
        users = result.scalars().all()

        if not users:
            logger.info(f"No targeted officials found for alert {alert_id} in district {district_id}")
            return

        logger.info(f"Targeting {len(users)} officials for alert {alert_id}")

        for user in users:
            # We now pass user_email specifically instead of a generic broadcast
            await send_alert_notification(
                alert_id=alert_id,
                district_name=district_name,
                disease=disease,
                risk_score=risk_score,
                user_email=user.email
            )

# Wire up the subscription
bus.subscribe("prediction.high_risk", handle_high_risk_prediction)
