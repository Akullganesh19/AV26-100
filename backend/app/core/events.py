import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._background_tasks: set[asyncio.Task] = set()

    def on(self, event_name: str):
        """Decorator to register a listener for an event."""
        def decorator(func: Callable):
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(func)
            return func
        return decorator

    def emit(self, event_name: str, *args, **kwargs):
        """Emits an event, triggering all registered listeners asynchronously."""
        if event_name not in self._listeners:
            return

        for listener in self._listeners[event_name]:
            task = asyncio.create_task(self._safe_execute(listener, *args, **kwargs))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    async def _safe_execute(self, listener: Callable, *args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(listener):
                await listener(*args, **kwargs)
            else:
                listener(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing listener for event: {str(e)}", exc_info=True)

event_bus = EventBus()
