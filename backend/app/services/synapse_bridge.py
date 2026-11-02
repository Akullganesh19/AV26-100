from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any
from app.models.user import User
from app.models.user_district import user_district_association
import logging

logger = logging.getLogger(__name__)

async def enrich_alert_with_officers(db: AsyncSession, district_id: str, risk_score: float) -> List[Dict[str, Any]]:
    """
    Synapse Connection: Auth ↔ Alerts
    Finds officers responsible for the affected district who have email_alerts enabled
    and whose personal alert_threshold is <= the incident's risk score.
    """
    try:
        # Explicit conversion to float as risk_score can be string or Decimal
        risk_score_float = float(risk_score)
    except (ValueError, TypeError):
        logger.error(f"Invalid risk score passed to synapse bridge: {risk_score}")
        return []

    query = select(User).join(
        user_district_association, User.id == user_district_association.c.user_id
    ).where(
        and_(
            user_district_association.c.district_id == district_id,
            User.email_alerts == True,
            User.alert_threshold <= int(risk_score_float),
            User.is_active == True
        )
    )

    result = await db.execute(query)
    users = result.scalars().all()

    return [{"id": str(u.id), "name": u.name, "email": u.email, "threshold": u.alert_threshold} for u in users]
