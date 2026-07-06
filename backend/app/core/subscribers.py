import logging
from sqlalchemy import select, and_

from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

async def handle_high_risk_prediction(prediction_id: str, district_id: str, disease: str, risk_score: float) -> None:
    """
    Subscriber for prediction.high_risk events.
    Finds targeted users assigned to the district and dispatches notifications if thresholds are met.
    """
    logger.info(f"EventBus: Processing high_risk prediction {prediction_id} for district {district_id}")

    async with SessionLocal() as db:
        try:
            # 1. Fetch District Name
            district = await db.get(District, district_id)
            district_name = district.name if district else str(district_id)

            # 2. Query targeted users assigned to this district who have alerts enabled and meet the threshold
            query = (
                select(User)
                .join(User.districts)
                .where(
                    and_(
                        District.id == district_id,
                        User.email_alerts == True,
                        User.alert_threshold <= risk_score # risk_score is 0-100
                    )
                )
            )
            result = await db.execute(query)
            users_to_notify = result.scalars().all()

            if not users_to_notify:
                logger.info(f"EventBus: No users to notify for prediction {prediction_id}")
                return

            # 3. Dispatch targeted alerts
            for user in users_to_notify:
                await send_alert_notification(
                    alert_id=prediction_id,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score,
                    user_email=user.email
                )

        except Exception as e:
            logger.error(f"EventBus: Error processing handle_high_risk_prediction: {e}", exc_info=True)

# Register the subscriber
event_bus.subscribe("prediction.high_risk", handle_high_risk_prediction)
logger.info("EventBus: Subscribers registered.")
