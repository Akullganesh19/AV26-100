import logging
from sqlalchemy import select
from uuid import UUID
from app.core.database import SessionLocal
from app.models.district import District
from app.models.user import User
from app.tasks.alerts import send_targeted_alert

logger = logging.getLogger(__name__)

async def route_high_risk_alert(prediction_id: str, district_id: UUID, disease: str, risk_score: float):
    """
    Listens for high risk prediction events and routes targeted alerts to users
    subscribed to the affected district whose alert threshold is met.
    """
    logger.info(f"Routing high risk alert for prediction {prediction_id} (District: {district_id})")

    async with SessionLocal() as db:
        # Fetch district name
        district = await db.get(District, district_id)
        if not district:
            logger.error(f"District {district_id} not found when routing alert")
            return
        district_name = district.name

        # Find users subscribed to this district who have email alerts enabled
        query = (
            select(User)
            .join(User.districts)
            .where(District.id == district_id)
            .where(User.email_alerts == True)
        )

        result = await db.execute(query)
        users = result.scalars().all()

        # Dispatch targeted alerts based on user-specific thresholds
        dispatched_count = 0
        for user in users:
            # risk_score is e.g. 0.85, threshold is e.g. 70 (meaning 70%). Convert to comparable units.
            normalized_score = risk_score * 100
            if normalized_score >= user.alert_threshold:
                # Dispatch the targeted alert task
                from app.core.events import event_bus
                event_bus.create_task(
                    send_targeted_alert(
                        alert_id=prediction_id,
                        user_email=user.email,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score
                    )
                )
                dispatched_count += 1

        logger.info(f"Routed high risk alert {prediction_id} to {dispatched_count} users")
