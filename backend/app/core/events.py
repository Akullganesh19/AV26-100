import asyncio
import logging
from typing import Callable, Dict, List, Any, Set

logger = logging.getLogger(__name__)

class EventBus:
    """
    Lightweight, central EventBus for cross-system pub/sub.
    Manages strong references to asynchronous tasks to prevent premature garbage collection.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def on(self, event_type: str):
        """Decorator to register an event listener."""
        def decorator(func: Callable):
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(func)
            return func
        return decorator

    def emit(self, event_type: str, *args, **kwargs):
        """
        Emits an event, dispatching to all registered listeners asynchronously.
        """
        listeners = self._listeners.get(event_type, [])
        if not listeners:
            logger.debug(f"No listeners registered for event: {event_type}")
            return

        for listener in listeners:
            try:
                # Dispatch listener as an asyncio task
                task = asyncio.create_task(listener(*args, **kwargs))

                # Maintain strong reference
                self._background_tasks.add(task)

                # Attach callback to remove task upon completion
                task.add_done_callback(self._background_tasks.discard)
            except Exception as e:
                logger.error(f"Error dispatching listener for event {event_type}: {e}", exc_info=True)

# Global event bus instance
event_bus = EventBus()
