import logging
from sqlalchemy import select
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

async def notify_users_of_alert(alert_data: dict):
    """
    Listens to 'alert.created' and emails users linked to that district.
    """
    district_id_str = alert_data.get("district_id")
    disease = alert_data.get("disease")
    risk_score = alert_data.get("risk_score")
    alert_type = alert_data.get("alert_type")

    if not district_id_str:
        return

    logger.info(f"Event received: alert.created for district {district_id_str}")

    async with SessionLocal() as db:
        try:
            # First, fetch district name
            district_query = select(District).where(District.id == district_id_str)
            result_district = await db.execute(district_query)
            district = result_district.scalar_one_or_none()
            district_name = district.name if district else "Unknown District"

            # Fetch users who want emails for this district
            query = (
                select(User)
                .join(user_district_association)
                .where(user_district_association.c.district_id == district_id_str)
                .where(User.email_alerts == True)
            )
            result = await db.execute(query)
            users = result.scalars().all()

            for user in users:
                logger.info(f"Sending health alert email to {user.email} for {disease} in {district_name}")
                await integration_service.send_health_alert_email(
                    to_email=user.email,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
        except Exception as e:
            logger.error(f"Failed to process alert notification: {str(e)}", exc_info=True)


# Register subscribers
event_bus.subscribe("alert.created", notify_users_of_alert)
