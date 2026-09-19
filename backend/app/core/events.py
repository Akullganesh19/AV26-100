import asyncio
import logging
from typing import Callable, Dict, List, Set

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._active_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_name: str, listener: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)

    def publish(self, event_name: str, *args, **kwargs):
        for listener in self._listeners.get(event_name, []):
            if asyncio.iscoroutinefunction(listener):
                task = asyncio.create_task(listener(*args, **kwargs))
                self._active_tasks.add(task)
                task.add_done_callback(self._active_tasks.discard)
            else:
                try:
                    listener(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_name}: {e}")

event_bus = EventBus()
