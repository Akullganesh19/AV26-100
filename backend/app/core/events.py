import asyncio
import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, *args, **kwargs):
        if event_name not in self._subscribers:
            return

        for callback in self._subscribers[event_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(callback(*args, **kwargs))
                    except RuntimeError:
                        # If no running loop, we can't easily schedule the task
                        # but typically we're in FastAPI where a loop exists
                        logger.error("No running event loop to create task for async subscriber.")
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in subscriber {callback.__name__} for event {event_name}: {e}", exc_info=True)

event_bus = EventBus()
