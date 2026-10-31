import asyncio
from typing import Any, Callable, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.district import District
from app.models.user_district import user_district_association
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

# Strong references for fire-and-forget background tasks
_background_tasks = set()

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def emit(self, event_type: str, **kwargs):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                # Run callbacks in the background
                task = asyncio.create_task(callback(**kwargs))
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)

event_bus = EventBus()

async def route_alert_to_officers(alert_id: str, district_id: str, disease: str, risk_score: float):
    """
    Listens to 'alert.triggered' and routes to officers based on User settings.
    """
    try:
        async with SessionLocal() as db:
            # Fetch users assigned to this district who have email alerts ON
            # and a threshold <= the current risk score
            query = (
                select(User)
                .join(user_district_association, User.id == user_district_association.c.user_id)
                .where(
                    and_(
                        user_district_association.c.district_id == district_id,
                        User.email_alerts == True,
                        User.alert_threshold <= (risk_score * 100),
                        User.is_active == True
                    )
                )
            )

            result = await db.execute(query)
            users = result.scalars().all()

            # Also fetch sysadmins as fallback
            admin_query = select(User).where(and_(User.role == UserRole.SYSADMIN, User.email_alerts == True))
            admin_result = await db.execute(admin_query)
            admins = admin_result.scalars().all()

            target_users = list(set(users + admins))
            emails = [u.email for u in target_users]

            if emails:
                # Fetch District Name
                dist_result = await db.execute(select(District.name).where(District.id == district_id))
                district_name = dist_result.scalar() or str(district_id)

                logger.info(f"SYNAPSE: Routing alert {alert_id} to {len(emails)} users: {emails}")

                task = asyncio.create_task(send_alert_notification(
                    alert_id=alert_id,
                    district_name=district_name,
                    disease=disease,
                    risk_score=risk_score,
                    targets=emails
                ))
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)
            else:
                logger.info(f"SYNAPSE: No matching officers found for alert {alert_id} in {district_id}")
    except Exception as e:
        logger.error(f"SYNAPSE ROUTING FAILED: {str(e)}", exc_info=True)

# Register subscribers
event_bus.subscribe("alert.triggered", route_alert_to_officers)
