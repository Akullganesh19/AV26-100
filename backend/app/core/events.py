import asyncio
import logging
from typing import Callable, Awaitable, Dict, List, Set, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[..., Awaitable[None]]]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, handler: Callable[..., Awaitable[None]]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")

    def publish(self, event_type: str, **kwargs):
        handlers = self.subscribers.get(event_type, [])
        for handler in handlers:
            task = asyncio.create_task(handler(**kwargs))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
            logger.info(f"Published event {event_type} to handler")

event_bus = EventBus()
