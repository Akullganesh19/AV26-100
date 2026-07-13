import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._background_tasks = set()

    def on(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def emit(self, event_type: str, *args, **kwargs):
        logger.info(f"EventBus emitting: {event_type}")
        if event_type not in self._subscribers:
            return
        for callback in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                task = asyncio.create_task(callback(*args, **kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in sync event callback: {e}", exc_info=True)

event_bus = EventBus()
