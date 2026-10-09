import asyncio
from typing import Callable, Dict, List, Any, Awaitable
import logging

logger = logging.getLogger(__name__)

# Strong references for fire-and-forget tasks
background_tasks = set()

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[..., Awaitable[None]]]] = {}

    def subscribe(self, event_type: str, callback: Callable[..., Awaitable[None]]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type: str, data: Any):
        logger.info(f"EventBus publishing: {event_type}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                task = asyncio.create_task(self._run_callback(callback, event_type, data))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

    async def _run_callback(self, callback: Callable[..., Awaitable[None]], event_type: str, data: Any):
        try:
            await callback(data)
        except Exception as e:
            logger.error(f"Error in event subscriber for {event_type}: {e}", exc_info=True)

event_bus = EventBus()
