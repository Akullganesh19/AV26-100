import asyncio
from collections import defaultdict
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)

    def on(self, event_name: str, listener: Callable):
        self._listeners[event_name].append(listener)
        logger.info(f"EventBus: Registered listener for event: {event_name}")

    async def emit(self, event_name: str, *args, **kwargs):
        listeners = self._listeners.get(event_name, [])
        if not listeners:
            return
        logger.info(f"EventBus: Emitting event: {event_name} to {len(listeners)} listeners")
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(*args, **kwargs)
                else:
                    listener(*args, **kwargs)
            except Exception as e:
                logger.error(f"EventBus: Error in event listener for {event_name}: {e}", exc_info=True)

event_bus = EventBus()
