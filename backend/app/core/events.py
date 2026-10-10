import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.background_tasks = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type: str, *args, **kwargs):
        if event_type in self.subscribers:
            logger.info(f"Publishing event {event_type} to {len(self.subscribers[event_type])} subscribers")
            for callback in self.subscribers[event_type]:
                task = asyncio.create_task(callback(*args, **kwargs))
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)

event_bus = EventBus()
