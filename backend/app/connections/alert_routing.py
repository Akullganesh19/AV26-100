import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def route_alert_to_subscribers(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Synapse Connection: Routes autonomous alerts to users based on their
    district subscriptions and personalized risk thresholds.
    """
    logger.info(f"SYNAPSE: Received prediction.high_risk event for district {district_id} ({disease})")

    async with SessionLocal() as db:
        district = await db.get(District, district_id)
        district_name = district.name if district else str(district_id)

        # Correlation: Find users who care about this district AND meet threshold
        # Note: risk_score is a float between 0 and 1, alert_threshold is an int 0-100
        query = (
            select(User)
            .join(User.districts)
            .where(District.id == district_id)
            .where(User.email_alerts == True)
            .where(User.alert_threshold <= (risk_score * 100))
            .where(User.is_active == True)
        )
        result = await db.execute(query)
        users = result.scalars().all()

        if users:
            logger.info(f"SYNAPSE: Correlated {len(users)} target users for {district_name}")
            for user in users:
                logger.info(f"SYNAPSE: Dispatching to User {user.email} (Threshold {user.alert_threshold} <= Risk {risk_score * 100})")
                await send_alert_notification(
                    alert_id=alert_id,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score,
                    user_email=user.email
                )
        else:
            logger.info(f"SYNAPSE: No users met threshold correlation for {district_name}")
            # Fallback for generic system alert if no user matched
            await send_alert_notification(
                alert_id=alert_id,
                district_name=district_name,
                disease=disease,
                risk_score=risk_score
            )

def setup_connections(event_bus):
    event_bus.on("prediction.high_risk", route_alert_to_subscribers)
