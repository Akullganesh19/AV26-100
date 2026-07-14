import asyncio
import logging
from typing import Callable, Dict, List, Coroutine, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Coroutine[Any, Any, None]]]] = {}
        self._background_tasks = set()

    def on(self, event_name: str, listener: Callable[..., Coroutine[Any, Any, None]]):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)
        logger.debug(f"Registered listener for event: {event_name}")

    def emit(self, event_name: str, *args, **kwargs):
        if event_name not in self._listeners:
            return

        for listener in self._listeners[event_name]:
            try:
                task = asyncio.create_task(listener(*args, **kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            except Exception as e:
                logger.error(f"Failed to dispatch event {event_name}: {e}")

event_bus = EventBus()
