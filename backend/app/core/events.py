import asyncio
import logging
from typing import Callable, Any, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_type: str, callback: Callable[..., Any]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}. Total listeners: {len(self._listeners[event_type])}")

    def publish(self, event_type: str, *args, **kwargs):
        if event_type not in self._listeners:
            return
        for callback in self._listeners[event_type]:
            if asyncio.iscoroutinefunction(callback):
                asyncio.create_task(callback(*args, **kwargs))
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {e}", exc_info=True)

event_bus = EventBus()
