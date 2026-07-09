import asyncio
import logging
from typing import Callable, Dict, List, Any, Set, Awaitable

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        # Keep a strong reference to async tasks to prevent garbage collection mid-execution
        self._tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed {callback.__name__} to event '{event_type}'")

    def publish(self, event_type: str, *args, **kwargs) -> None:
        if event_type not in self._subscribers:
            logger.debug(f"No subscribers for event '{event_type}'")
            return

        for callback in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                task = asyncio.create_task(callback(*args, **kwargs))
                self._tasks.add(task)
                # Remove task from the set once completed
                task.add_done_callback(self._tasks.discard)
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in synchronous subscriber {callback.__name__} for event {event_type}: {e}", exc_info=True)

event_bus = EventBus()
