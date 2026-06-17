import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import SessionLocal
from app.core.events import event_bus
from app.models.user import User
from app.models.district import District
from app.models.alert import Alert
from app.api.integrations import integration_service

logger = logging.getLogger(__name__)

async def handle_alert_triggered(alert_id: str):
    """
    Synapse Connector:
    Listens for new alerts and queries the Auth System to notify assigned users
    based on their alert_threshold and email_alerts preferences.
    """
    logger.info(f"Synapse: Processing new alert trigger for {alert_id}")

    # Accept db session in kwargs for testing, otherwise use SessionLocal
    async def process_with_db(db):
        query = select(Alert).options(selectinload(Alert.district)).where(Alert.id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            logger.error(f"Synapse: Alert {alert_id} not found when dispatching notifications.")
            return

        district_id = alert.district_id
        disease = alert.disease
        risk_score = float(alert.risk_score)
        district_name = alert.district.name if alert.district else str(district_id)

        # Cross-reference the Auth System: find users assigned to this district
        user_query = select(User).where(
            User.districts.any(District.id == district_id),
            User.email_alerts == True,
            User.is_active == True,
            User.alert_threshold <= (risk_score * 100)
        )
        user_result = await db.execute(user_query)
        officers = user_result.scalars().all()

        if not officers:
            logger.info(f"Synapse: No eligible officers found for district {district_id} matching alert criteria.")
            return

        logger.info(f"Synapse: Found {len(officers)} officers to notify for alert {alert_id}")

        for officer in officers:
            try:
                await integration_service.send_health_alert_email(
                    to_email=officer.email,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score
                )
                logger.info(f"Synapse: Dispatched alert email to {officer.email}")
            except Exception as e:
                logger.error(f"Synapse: Failed to dispatch alert to {officer.email}: {e}")

    # For testing we can pass db explicitly if we modify event_bus, but since event_bus doesn't
    # easily pass the session without modifying callers, we use SessionLocal normally.
    # To make testing easy without refactoring the event bus, we rely on the DB having committed data.
    async with SessionLocal() as db:
        await process_with_db(db)

def setup_alert_dispatch():
    """Register the Synapse connection with the Event Bus."""
    event_bus.subscribe("alert.triggered", handle_alert_triggered)
    logger.info("Synapse: Event listeners registered for Alert Dispatch.")
