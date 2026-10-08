import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._background_tasks = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, *args: Any, **kwargs: Any):
        logger.info(f"EventBus: Publishing event {event_type}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        task = asyncio.create_task(callback(*args, **kwargs))
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"EventBus: Error in subscriber for {event_type}: {e}")

event_bus = EventBus()
