import asyncio
import logging
from typing import Callable, Any, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        # Keep strong references to background tasks per asyncio requirements
        self._background_tasks = set()

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
        logger.debug(f"Subscribed to event {event_name}")

    def emit(self, event_name: str, *args, **kwargs):
        if event_name not in self._listeners:
            return

        for callback in self._listeners[event_name]:
            if asyncio.iscoroutinefunction(callback):
                async def _run_async_callback(cb, *a, **kw):
                    try:
                        await cb(*a, **kw)
                    except Exception as e:
                        logger.error(f"Error in async event listener for {event_name}: {e}", exc_info=True)

                task = asyncio.create_task(_run_async_callback(callback, *args, **kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in sync event listener for {event_name}: {e}", exc_info=True)

# Global event bus instance
event_bus = EventBus()
