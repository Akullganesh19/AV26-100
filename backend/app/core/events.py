import asyncio
import logging
from typing import Callable, Dict, List, Any, Set

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def on(self, event_type: str):
        def decorator(func: Callable):
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(func)
            return func
        return decorator

    def emit(self, event_type: str, *args, **kwargs):
        if event_type not in self.listeners:
            return

        for listener in self.listeners[event_type]:
            if asyncio.iscoroutinefunction(listener):
                task = asyncio.create_task(listener(*args, **kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                try:
                    listener(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {e}", exc_info=True)

event_bus = EventBus()
