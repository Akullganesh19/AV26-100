import asyncio
from typing import Callable, Any, Dict

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event_type: str, **kwargs):
        if not hasattr(self, '_background_tasks'):
            self._background_tasks = set()

        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                task = asyncio.create_task(handler(**kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)

event_bus = EventBus()
