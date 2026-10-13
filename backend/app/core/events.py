import asyncio
import logging
from collections import defaultdict
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._background_tasks = set()

    def subscribe(self, event_type: str, handler: Callable):
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type}")

    def publish(self, event_type: str, *args, **kwargs):
        handlers = self._subscribers.get(event_type, [])
        logger.debug(f"Publishing {event_type} to {len(handlers)} handlers")
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                task = asyncio.create_task(handler(*args, **kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)

event_bus = EventBus()
