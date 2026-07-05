import asyncio
from typing import Callable, Dict, List, Any, Set
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        # Keep strong references to tasks to prevent GC before completion
        self._tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed {callback.__name__} to {event_type}")

    def emit(self, event_type: str, **kwargs):
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(**kwargs))
                    self._tasks.add(task)
                    task.add_done_callback(self._tasks.discard)
                else:
                    callback(**kwargs)
            except Exception as e:
                logger.error(f"Error in subscriber {callback.__name__} for event {event_type}: {e}", exc_info=True)

event_bus = EventBus()
