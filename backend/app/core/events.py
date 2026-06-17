import asyncio
import logging
from typing import Callable, Awaitable, Any, Dict

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, list[Callable[..., Awaitable[None]]]] = {}

    def subscribe(self, event_name: str, callback: Callable[..., Awaitable[None]]):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
        logger.debug(f"Subscribed to event {event_name}")

    async def publish(self, event_name: str, *args, **kwargs):
        if event_name not in self._subscribers:
            return

        logger.debug(f"Publishing event {event_name}")
        tasks = []
        for callback in self._subscribers[event_name]:
            tasks.append(asyncio.create_task(self._safe_execute(event_name, callback, *args, **kwargs)))

        if tasks:
            await asyncio.gather(*tasks)

    async def _safe_execute(self, event_name: str, callback: Callable, *args, **kwargs):
        try:
            await callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in event handler for {event_name}: {e}", exc_info=True)

event_bus = EventBus()
