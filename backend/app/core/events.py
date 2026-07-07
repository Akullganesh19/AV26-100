import asyncio
import inspect
from typing import Callable, Dict, List, Any, Set

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, **kwargs: Any):
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            if inspect.iscoroutinefunction(callback):
                task = asyncio.create_task(callback(**kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                callback(**kwargs)

event_bus = EventBus()
