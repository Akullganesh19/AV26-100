from typing import Callable, Dict, List
import asyncio

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.background_tasks = set()

    def on(self, event_name: str, listener: Callable):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def emit(self, event_name: str, **kwargs):
        if event_name in self.listeners:
            for listener in self.listeners[event_name]:
                # Execute async listener without awaiting to prevent blocking the emitter
                task = asyncio.create_task(listener(**kwargs))
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)

event_bus = EventBus()
