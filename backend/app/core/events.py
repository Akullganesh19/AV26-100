import asyncio
from typing import Callable, Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event_type: str, listener: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        logger.debug(f"Registered listener for event: {event_type}")

    async def emit(self, event_type: str, *args, **kwargs):
        logger.info(f"EventBus emitting: {event_type}")
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        # Create task to avoid blocking the event loop
                        asyncio.create_task(listener(*args, **kwargs))
                    else:
                        listener(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in listener for event {event_type}: {e}", exc_info=True)

event_bus = EventBus()
