from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.models.user import User
from app.models.district import District

class IntelligenceBridge:
    """
    Synapse Intelligence Bridge: Connects the Auth/User Domain with the Alert Domain.
    Uses the Enrichment Pattern to supply cross-system context without tight coupling.
    """

    @staticmethod
    async def get_targeted_officers(db: AsyncSession, district_id: str | UUID, risk_score: float) -> list[dict]:
        """
        Intelligence: Only notify users who are actively monitoring the affected district,
        have email alerts enabled, and whose personalized threshold is met by the current risk.
        """
        query = (
            select(User)
            .join(User.districts)
            .where(
                and_(
                    District.id == district_id,
                    User.is_active == True,
                    User.email_alerts == True,
                    User.alert_threshold <= risk_score
                )
            )
        )

        result = await db.execute(query)
        users = result.scalars().all()

        return [{"id": str(u.id), "name": u.name, "email": u.email, "threshold": u.alert_threshold} for u in users]
