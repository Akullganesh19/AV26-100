import asyncio
import logging
from typing import Callable, Coroutine, Any, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable[..., Coroutine[Any, Any, None]]]] = {}
        self._tasks: set[asyncio.Task] = set()

    def on(self, event_name: str, handler: Callable[..., Coroutine[Any, Any, None]]):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(handler)
        logger.info(f"Registered listener for event: {event_name}")

    def emit(self, event_name: str, **kwargs):
        if event_name not in self.listeners:
            logger.debug(f"No listeners found for event: {event_name}")
            return

        for handler in self.listeners[event_name]:
            task = asyncio.create_task(self._safe_execute(handler, event_name, **kwargs))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    def create_task(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
        """Helper to create a fire-and-forget task with strong references."""
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def _safe_execute(self, handler, event_name, **kwargs):
        try:
            await handler(**kwargs)
        except Exception as e:
            logger.error(f"Error in event handler for {event_name}: {e}", exc_info=True)

event_bus = EventBus()
