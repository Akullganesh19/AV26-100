import asyncio
import inspect
from typing import Any, Callable, Dict, List, Set

class EventBus:
    """
    A simple in-memory event bus supporting synchronous and asynchronous subscribers.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        # Keep strong references to background tasks so they aren't garbage collected
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, **kwargs: Any) -> None:
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                task = asyncio.create_task(callback(**kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                callback(**kwargs)

# Global event bus instance
event_bus = EventBus()
