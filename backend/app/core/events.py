import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._tasks = set()

    def subscribe(self, event_name: str, handler: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(handler)

    def emit(self, event_name: str, *args, **kwargs):
        handlers = self._subscribers.get(event_name, [])
        if not handlers:
            return

        for handler in handlers:
            task = asyncio.create_task(self._safe_execute(handler, *args, **kwargs))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    async def _safe_execute(self, handler: Callable, *args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                await asyncio.to_thread(handler, *args, **kwargs)
        except Exception as e:
            logger.error(f"Event handler {handler.__name__} failed: {e}", exc_info=True)

event_bus = EventBus()
