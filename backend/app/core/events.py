import inspect
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to {event_type}")

    async def publish(self, event_type: str, data: Any):
        logger.info(f"EventBus publishing {event_type}")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    result = callback(data)
                    if inspect.isawaitable(result):
                        await result
                except Exception as e:
                    logger.error(f"Error processing event {event_type} in {callback.__name__}: {e}", exc_info=True)

event_bus = EventBus()
