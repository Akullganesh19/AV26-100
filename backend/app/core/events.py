import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type: str, data: Any):
        if event_type in self._subscribers:
            logger.info(f"EventBus publishing '{event_type}' to {len(self._subscribers[event_type])} subscribers")
            for callback in self._subscribers[event_type]:
                # If it's a coroutine function, schedule it
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(data))
                else:
                    try:
                        callback(data)
                    except Exception as e:
                        logger.error(f"Error in subscriber for {event_type}: {e}")
        else:
            logger.debug(f"No subscribers for {event_type}")

# Singleton instance
event_bus = EventBus()
