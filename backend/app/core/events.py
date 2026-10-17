import asyncio
import logging
import inspect
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._background_tasks = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event {event_type}")

    def publish(self, event_type: str, **kwargs: Any):
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            task = asyncio.create_task(self._safe_execute(callback, **kwargs))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    async def _safe_execute(self, callback: Callable, **kwargs):
        try:
            result = callback(**kwargs)
            if inspect.isawaitable(result):
                await result
        except Exception as e:
            logger.error(f"Error in event subscriber: {str(e)}", exc_info=True)

event_bus = EventBus()
