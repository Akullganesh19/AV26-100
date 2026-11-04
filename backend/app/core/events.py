import asyncio
import logging
import inspect
from typing import Callable, Dict, List, Any, Set

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_name: str, listener: Callable):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def emit(self, event_name: str, *args: Any, **kwargs: Any):
        if event_name in self.listeners:
            for listener in self.listeners[event_name]:
                try:
                    result = listener(*args, **kwargs)
                    if inspect.isawaitable(result):
                        task = asyncio.create_task(result)
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_name}: {e}")

event_bus = EventBus()
