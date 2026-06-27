import asyncio
from typing import Callable, Dict, List
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, *args, **kwargs):
        logger.info(f"EventBus publishing event: {event_name}")
        if event_name not in self._subscribers:
            return

        for callback in self._subscribers[event_name]:
            if asyncio.iscoroutinefunction(callback):
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(callback(*args, **kwargs))
                except RuntimeError:
                    asyncio.run(callback(*args, **kwargs))
            else:
                callback(*args, **kwargs)

bus = EventBus()
