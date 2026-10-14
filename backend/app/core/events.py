import asyncio
import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

_background_tasks = set()


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed to {event_type}")

    def publish(self, event_type: str, *args, **kwargs):
        logger.info(f"Publishing event: {event_type}")
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                task = asyncio.create_task(handler(*args, **kwargs))
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)


event_bus = EventBus()


async def handle_alert_triggered(alert_id: str):
    logger.info(f"EventBus: Handling alert_triggered for alert {alert_id}")
    from app.core.database import SessionLocal
    from sqlalchemy import select
    from app.models.user import User
    from app.models.district import District
    from app.models.alert import Alert
    from app.api.integrations import integration_service

    async with SessionLocal() as db:
        result = await db.execute(
            select(Alert, District.name)
            .join(District, Alert.district_id == District.id)
            .where(Alert.id == alert_id)
        )
        row = result.first()
        if not row:
            return
        alert, district_name = row

        score = float(alert.risk_score)
        normalized_score = score * 100 if score <= 1.0 else score

        users_result = await db.execute(
            select(User).join(User.districts).where(
                District.id == alert.district_id,
                User.email_alerts.is_(True),
                User.alert_threshold <= normalized_score
            )
        )
        users = users_result.scalars().all()

        for user in users:
            await integration_service.send_health_alert_email(
                to_email=user.email,
                district_name=district_name,
                disease=alert.disease,
                risk_score=score
            )


def setup_subscribers():
    event_bus.subscribe("alert.triggered", handle_alert_triggered)
