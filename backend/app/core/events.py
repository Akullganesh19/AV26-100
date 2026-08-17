import asyncio
import logging
from collections import defaultdict
from typing import Callable, Any, Awaitable

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)

    def on(self, event_type: str, callback: Callable[..., Awaitable[Any]]):
        self._listeners[event_type].append(callback)

    def emit(self, event_type: str, **kwargs):
        logger.info(f"EVENT_BUS: Emitting {event_type}")
        for callback in self._listeners.get(event_type, []):
            asyncio.create_task(callback(**kwargs))

event_bus = EventBus()
