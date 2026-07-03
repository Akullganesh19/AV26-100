import asyncio
from typing import Callable, Dict, List, Set

class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers = {}
            cls._instance._tasks = set()
        return cls._instance

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, *args, **kwargs):
        if event_name not in self._subscribers:
            return

        for callback in self._subscribers[event_name]:
            if asyncio.iscoroutinefunction(callback):
                task = asyncio.create_task(callback(*args, **kwargs))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
            else:
                callback(*args, **kwargs)

event_bus = EventBus()
