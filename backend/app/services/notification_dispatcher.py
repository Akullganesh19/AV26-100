import logging
import asyncio
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.user_district import user_district_association
from app.models.district import District

logger = logging.getLogger(__name__)

@event_bus.on("prediction.high_risk")
async def handle_high_risk_prediction(prediction_data: dict):
    """
    Listens for high risk prediction events and notifies relevant users.
    prediction_data should contain:
    - district_id (UUID)
    - disease (str)
    - risk_score (float, 0-100 scale)
    - alert_id (str)
    """
    district_id = prediction_data.get("district_id")
    disease = prediction_data.get("disease")
    risk_score = prediction_data.get("risk_score")
    alert_id = prediction_data.get("alert_id")

    if not all([district_id, disease, risk_score]):
        logger.error("Missing required prediction data for targeted notification.", extra={"data": prediction_data})
        return

    async with SessionLocal() as db:
        try:
            # Join users with user_districts to find users associated with the district
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(
                    and_(
                        user_district_association.c.district_id == district_id,
                        User.is_active == True,
                        User.email_alerts == True,
                        User.alert_threshold <= risk_score
                    )
                )
            )
            result = await db.execute(query)
            affected_users = result.scalars().all()

            if affected_users:
                logger.info(
                    f"Dispatched targeted notifications for alert {alert_id} to {len(affected_users)} users.",
                    extra={
                        "district_id": str(district_id),
                        "disease": disease,
                        "risk_score": risk_score,
                        "user_emails": [u.email for u in affected_users]
                    }
                )
                # In a real system, we'd send emails or push notifications here.
                # For this connection, logging it as simulated dispatch is sufficient.

        except Exception as e:
            logger.error(f"Error dispatching targeted notifications for {alert_id}: {e}", exc_info=True)
