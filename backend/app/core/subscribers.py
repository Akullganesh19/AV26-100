import logging
from sqlalchemy import select, and_
from app.core.events import event_bus
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

async def on_alert_triggered(*args, **kwargs):
    alert_id = kwargs.get("alert_id")
    district_id = kwargs.get("district_id")
    disease = kwargs.get("disease")
    risk_score = kwargs.get("risk_score")

    if not all([alert_id, district_id, disease, risk_score is not None]):
        logger.warning(f"Missing data in alert.triggered event: {kwargs}")
        return

    try:
        async with SessionLocal() as db:
            # Query users who track this district, have email_alerts enabled, and whose threshold is met
            stmt = (
                select(User, District)
                .join(User.districts)
                .where(
                    and_(
                        District.id == district_id,
                        User.email_alerts == True,
                        User.alert_threshold <= (risk_score * 100)
                    )
                )
            )
            result = await db.execute(stmt)
            users_and_districts = result.all()

            for user, district in users_and_districts:
                logger.info(f"Sending alert email to user {user.id} for alert {alert_id}")
                await integration_service.send_health_alert_email(
                    to_email=user.email,
                    district_name=district.name,
                    disease=disease,
                    risk_score=risk_score
                )
    except Exception as e:
        logger.error(f"Error processing alert.triggered event: {e}", exc_info=True)

event_bus.subscribe("alert.triggered", on_alert_triggered)
