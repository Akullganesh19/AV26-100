import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.district import District
from app.models.alert import Alert
from app.tasks.alerts import send_alert_notification
from typing import Any

logger = logging.getLogger(__name__)

async def dispatch_targeted_alerts(db: AsyncSession, alert: Alert, district_name: str) -> None:
    """
    Finds users assigned to the alert's district who have email_alerts enabled
    and whose alert_threshold is met by the alert's risk_score.
    """
    try:
        # Convert the float 0.0-1.0 to 0-100 percentage for comparison if needed
        # Assuming risk_score is mostly < 1.0 (e.g., 0.88), if it's already a percentage (e.g. 88.0), we just compare
        score_pct = float(alert.risk_score) if float(alert.risk_score) > 1.0 else float(alert.risk_score) * 100

        query = (
            select(User)
            .filter(
                User.districts.any(District.id == alert.district_id),
                User.email_alerts == True,
                User.alert_threshold <= score_pct,
                User.is_active == True
            )
        )
        result = await db.execute(query)
        users = result.scalars().all()

        logger.info(f"Dispatching alert {alert.id} to {len(users)} targeted users in district {alert.district_id}")

        for user in users:
            # We add user_id to the payload to make the dispatch targeted
            await send_alert_notification(
                alert_id=str(alert.id),
                district_name=district_name,
                disease=alert.disease,
                risk_score=float(alert.risk_score),
                user_id=str(user.id)
            )

    except Exception as e:
        logger.error(f"Failed to dispatch targeted alerts for {alert.id}: {str(e)}", exc_info=True)
