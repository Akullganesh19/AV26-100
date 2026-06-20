import logging
from typing import Any
from app.core.events import event_bus
from app.api.integrations import integration_service
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def handle_alert_triggered(
    alert_id: str, district_id: str, disease: str, risk_score: float, **kwargs: Any
):
    """
    Event handler for cross-system intelligence.
    Listens for high risk predictions and clinical cluster alerts,
    finds relevant users from Auth, and selectively notifies them.
    """
    logger.info(
        f"Received alert.triggered event for {alert_id} in {district_id} ({disease})"
    )

    try:
        async with SessionLocal() as db:
            # Get district name
            district_result = await db.execute(
                select(District).where(District.id == district_id)
            )
            district = district_result.scalar_one_or_none()
            district_name = district.name if district else "Unknown District"

            # Cross-System Join: Find users assigned to this district
            # who want email alerts and whose threshold is exceeded
            query = (
                select(User)
                .join(User.districts)
                .where(
                    User.email_alerts == True,
                    User.is_active == True,
                    User.alert_threshold
                    <= (risk_score * 100),  # Compare 0-100 threshold to score
                    District.id == district_id,
                )
            )

            result = await db.execute(query)
            targeted_users = result.scalars().all()

            logger.info(
                f"Found {len(targeted_users)} targeted users for alert {alert_id}"
            )

            for user in targeted_users:
                # Dispatch notification using integration service
                try:
                    await integration_service.send_health_alert_email(
                        to_email=user.email,
                        district_name=district_name,
                        disease=disease,
                        risk_score=risk_score,
                    )
                    logger.info(f"Dispatched email to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to dispatch to {user.email}: {e}")

    except Exception as exc:
        logger.error(f"Event handler failed for {alert_id}: {str(exc)}", exc_info=True)


# Subscribe to the events
event_bus.subscribe("alert.triggered", handle_alert_triggered)
event_bus.subscribe("prediction.high_risk", handle_alert_triggered)
