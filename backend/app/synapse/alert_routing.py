import logging
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.alert import Alert
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification
import asyncio

logger = logging.getLogger(__name__)

async def route_alert_to_officers(alert: Alert):
    """
    Intelligence Connection: Links autonomous alerts to specific health officers based on
    district assignment, communication preferences, and personal risk thresholds.
    """
    async with SessionLocal() as db:
        # Fetch alert details including district
        district_res = await db.execute(select(District).where(District.id == alert.district_id))
        district = district_res.scalar_one_or_none()
        district_name = district.name if district else str(alert.district_id)

        # Query users linked to this district who want email alerts and whose threshold is met
        query = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(
                user_district_association.c.district_id == alert.district_id,
                User.email_alerts == True,
                User.alert_threshold <= (alert.risk_score * 100)
            )
        )
        res = await db.execute(query)
        users = res.scalars().all()

        logger.info(f"Synapse routing alert {alert.id} to {len(users)} officers for district {district_name}")

        for user in users:
            # Dispatch personalized notification
            asyncio.create_task(send_alert_notification(
                alert_id=str(alert.id),
                district_name=district_name,
                disease=alert.disease,
                risk_score=float(alert.risk_score),
                user_email=user.email
            ))

# Subscribe to the event
event_bus.subscribe("alert.triggered", route_alert_to_officers)
