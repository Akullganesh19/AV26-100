import asyncio
import logging
from typing import Callable, Awaitable, Any, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Awaitable[None]]]] = {}
        self._tasks: set[asyncio.Task] = set()

    def on(self, event_name: str, callback: Callable[..., Awaitable[None]]):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, **kwargs: Any):
        listeners = self._listeners.get(event_name, [])
        for callback in listeners:
            task = asyncio.create_task(self._execute_callback(event_name, callback, kwargs))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    async def _execute_callback(self, event_name: str, callback: Callable[..., Awaitable[None]], kwargs: dict):
        try:
            logger.info(f"EventBus dispatching {event_name}")
            await callback(**kwargs)
        except Exception as e:
            logger.error(f"Error executing listener for {event_name}: {e}", exc_info=True)

event_bus = EventBus()
