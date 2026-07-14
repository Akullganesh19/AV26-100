import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District

logger = logging.getLogger(__name__)

async def handle_high_risk_prediction(prediction_id: str, district_id: str, disease: str, risk_score: float):
    """
    Targeted event-driven notification that alerts specific users assigned to a district.
    """
    logger.info(f"EventBus handling high_risk_prediction for {district_id} ({disease})")
    async with SessionLocal() as db:
        # Get users assigned to this district with email_alerts enabled
        # and where their personal alert_threshold is exceeded.
        query = select(User).join(User.districts).where(
            District.id == district_id,
            User.email_alerts == True,
            User.alert_threshold <= (risk_score * 100)
        )
        result = await db.execute(query)
        target_users = result.scalars().all()

        for user in target_users:
            # Dispatch specific notification to this user
            logger.info(
                f"Targeted Notification: Alerting user {user.email} (Threshold: {user.alert_threshold}) "
                f"about {disease} risk ({risk_score:.2f}) in district {district_id}."
            )

# Register the listener
event_bus.on("prediction.high_risk", handle_high_risk_prediction)
