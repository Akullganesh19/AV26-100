import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed to {event_type}")

    async def publish(self, event_type: str, payload: Any):
        if event_type not in self._subscribers:
            return

        logger.info(f"Publishing event {event_type}")
        handlers = self._subscribers[event_type]

        # Fire and forget handlers asynchronously so publisher isn't blocked
        for handler in handlers:
            asyncio.create_task(self._run_handler(event_type, handler, payload))

    async def _run_handler(self, event_type: str, handler: Callable, payload: Any):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)
        except Exception as e:
            logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)


event_bus = EventBus()
