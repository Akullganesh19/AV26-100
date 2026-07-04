import asyncio
import logging
from typing import Callable, Dict, List, Set, Any

logger = logging.getLogger(__name__)

class EventBus:
    """
    In-memory Event Bus for cross-system intelligence.
    Loosely couples disparate subsystems via pub/sub.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        # Maintain strong references to async tasks to prevent garbage collection
        # as noted in system memory guidelines.
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to event: {event_type}")

    def publish(self, event_type: str, *args: Any, **kwargs: Any):
        if event_type in self._subscribers:
            logger.debug(f"Publishing event: {event_type}")
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        task = asyncio.create_task(callback(*args, **kwargs))
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing subscriber for {event_type}: {e}", exc_info=True)

# Global Event Bus instance
bus = EventBus()
