import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.user import User
from app.models.user_district import user_district_association

logger = logging.getLogger(__name__)

class AlertRoutingIntelligence:
    """
    Synapse 🧠: Cross-System Intelligence
    Connects the Auth/User System (territories, preferences, thresholds)
    with the Alert/Monitoring System (outbreaks, clinical clusters).
    """

    @staticmethod
    async def get_targeted_recipients(db: AsyncSession, district_id: str, risk_score: float) -> list[str]:
        """
        Dynamically routes alerts only to users responsible for the affected district,
        who have opted into emails, and whose personal risk threshold is breached.
        """
        try:
            dist_uuid = uuid.UUID(str(district_id))
        except ValueError:
            logger.error(f"🧠 Synapse: Invalid district UUID format: {district_id}")
            return []

        normalized_score = risk_score if risk_score > 1.0 else risk_score * 100

        logger.info(f"🧠 Synapse: Routing alert for district {dist_uuid} (normalized score: {normalized_score})")

        query = (
            select(User.email)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(
                and_(
                    user_district_association.c.district_id == dist_uuid,
                    User.email_alerts == True,
                    User.alert_threshold <= normalized_score
                )
            )
        )

        result = await db.execute(query)
        emails = list(result.scalars().all())

        logger.info(f"🧠 Synapse: Yielded {len(emails)} targeted recipients for alert in district {dist_uuid}")
        return emails
