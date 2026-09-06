import asyncio
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.listeners = {}
            cls._instance.background_tasks = set()
        return cls._instance

    def on(self, event_name: str, callback: Callable):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)
        logger.info(f"Registered listener for event: {event_name}")

    def emit(self, event_name: str, **kwargs):
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        task = asyncio.create_task(callback(**kwargs))
                        self.background_tasks.add(task)
                        task.add_done_callback(self.background_tasks.discard)
                    else:
                        callback(**kwargs)
                except Exception as e:
                    logger.error(f"Error executing listener for {event_name}: {str(e)}", exc_info=True)

event_bus = EventBus()
