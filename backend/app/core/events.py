import asyncio
import logging
from typing import Callable, Dict, List, Set, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to event: {event_type}")

    def emit(self, event_type: str, *args: Any, **kwargs: Any):
        logger.debug(f"Emitting event: {event_type}")
        callbacks = self._subscribers.get(event_type, [])
        for callback in callbacks:
            if asyncio.iscoroutinefunction(callback):
                try:
                    task = asyncio.create_task(callback(*args, **kwargs))
                    self._tasks.add(task)
                    task.add_done_callback(self._tasks.discard)
                except Exception as e:
                    logger.error(f"Error creating task for {callback.__name__} on {event_type}: {e}", exc_info=True)
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing {callback.__name__} on {event_type}: {e}", exc_info=True)

    def on(self, event_type: str):
        """Decorator for subscribing to events."""
        def decorator(func: Callable):
            self.subscribe(event_type, func)
            return func
        return decorator

event_bus = EventBus()
