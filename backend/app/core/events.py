import asyncio
import inspect
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# Maintain a strong reference to active background tasks
_background_tasks = set()

class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._listeners = {}
        return cls._instance

    def on(self, event_type: str):
        """Register a callback for an event type via decorator."""
        def decorator(callback: Callable):
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(callback)
            logger.debug(f"Registered listener for event: {event_type}")
            return callback
        return decorator

    def emit(self, event_type: str, *args, **kwargs):
        """Emit an event to all registered listeners asynchronously."""
        if event_type not in self._listeners:
            return

        for callback in self._listeners[event_type]:
            if inspect.iscoroutinefunction(callback):
                task = asyncio.create_task(self._safe_execute_async(callback, *args, **kwargs))
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in synchronous event listener for {event_type}: {e}", exc_info=True)

    async def _safe_execute_async(self, callback: Callable, *args, **kwargs):
        try:
            await callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in asynchronous event listener for {callback.__name__}: {e}", exc_info=True)

# Global singleton instance
event_bus = EventBus()
