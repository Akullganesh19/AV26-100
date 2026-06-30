import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

async def notify_users_on_alert(alert_id: str, district_id: str, disease: str, risk_score: float):
    logger.info(f"Subscriber triggered for alert {alert_id} in district {district_id}")
    try:
        async with SessionLocal() as db:
            # Query the district name
            result_district = await db.execute(select(District).where(District.id == district_id))
            district = result_district.scalar_one_or_none()
            district_name = district.name if district else "Unknown District"

            # Query users associated with the district who have email_alerts enabled
            result_users = await db.execute(
                select(User)
                .join(User.districts)
                .where(District.id == district_id)
                .where(User.email_alerts == True)
            )
            users = result_users.scalars().all()

            for user in users:
                logger.info(f"Sending alert email to {user.email} for {disease} in {district_name}")
                await integration_service.send_health_alert_email(
                    to_email=user.email,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
    except Exception as e:
        logger.error(f"Error in notify_users_on_alert subscriber: {e}", exc_info=True)

# Register the subscriber
event_bus.subscribe('alert.triggered', notify_users_on_alert)
