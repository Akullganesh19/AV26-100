import asyncio
import logging
from typing import Callable, Dict, List, Set

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type: str, *args, **kwargs):
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(*args, **kwargs))
                    self._tasks.add(task)
                    task.add_done_callback(self._tasks.discard)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error publishing {event_type}: {e}", exc_info=True)

event_bus = EventBus()
