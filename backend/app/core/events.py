import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}
        self._background_tasks = set()

    def on(self, event_name: str, callback: Callable[..., Any]):
        """Register a callback for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
        logger.debug(f"Registered listener for event: {event_name}")

    def emit(self, event_name: str, *args, **kwargs):
        """Emit an event asynchronously, triggering all registered callbacks."""
        if event_name not in self._listeners:
            return

        for callback in self._listeners[event_name]:
            if asyncio.iscoroutinefunction(callback):
                task = asyncio.create_task(callback(*args, **kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing synchronous callback for {event_name}: {str(e)}", exc_info=True)

event_bus = EventBus()
