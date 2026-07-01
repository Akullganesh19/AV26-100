import asyncio
import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, *args, **kwargs):
        if event_type not in self.subscribers:
            return

        for callback in self.subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Safe way to schedule task in existing loop
                    loop = asyncio.get_running_loop()
                    loop.create_task(callback(*args, **kwargs))
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing subscriber for {event_type}: {e}", exc_info=True)

event_bus = EventBus()
