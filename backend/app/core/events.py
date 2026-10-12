import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._background_tasks = set()

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
        logger.info(f"Subscribed to event {event_name}")

    def publish(self, event_name: str, *args, **kwargs):
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(*args, **kwargs))
                    self._background_tasks.add(task)
                    task.add_done_callback(self._background_tasks.discard)
                else:
                    try:
                        callback(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Error in subscriber for {event_name}: {e}")

event_bus = EventBus()
