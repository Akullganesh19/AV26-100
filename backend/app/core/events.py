import asyncio
from typing import Callable, Dict, List, Any, Set
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """
    In-memory Event Bus to loosely couple domains.
    Supports both synchronous and asynchronous subscribers.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        # Keep strong references to background tasks to prevent garbage collection
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to event: {event_type}")

    def publish(self, event_type: str, *args, **kwargs):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        try:
                            # Try to get the running loop
                            loop = asyncio.get_running_loop()
                            task = loop.create_task(callback(*args, **kwargs))
                            self._background_tasks.add(task)
                            task.add_done_callback(self._background_tasks.discard)
                        except RuntimeError:
                            # If called from a synchronous thread (e.g. SQLAlchemy greenlet),
                            # we cannot create a task on the current non-existent loop.
                            asyncio.run(callback(*args, **kwargs))
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing subscriber {callback.__name__} for event {event_type}: {e}", exc_info=True)

# Global Event Bus instance
event_bus = EventBus()
