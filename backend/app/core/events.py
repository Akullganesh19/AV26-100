import asyncio
import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._active_tasks = set()

    def subscribe(self, event_type: str, listener: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def publish(self, event_type: str, *args, **kwargs):
        logger.info(f"EventBus: Publishing {event_type}")
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        task = asyncio.create_task(listener(*args, **kwargs))
                        # Prevent garbage collection of fire-and-forget tasks
                        self._active_tasks.add(task)
                        task.add_done_callback(self._active_tasks.discard)
                    else:
                        listener(*args, **kwargs)
                except Exception as e:
                    logger.error(f"EventBus error calling listener for {event_type}: {e}")

event_bus = EventBus()
