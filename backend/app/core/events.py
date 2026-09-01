import asyncio
import logging

logger = logging.getLogger(__name__)

class EventBus:
    _subscribers = {}
    _tasks = set()

    @classmethod
    def subscribe(cls, event_type: str, callback):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)

    @classmethod
    def publish(cls, event_type: str, *args, **kwargs):
        if event_type in cls._subscribers:
            for callback in cls._subscribers[event_type]:
                task = asyncio.create_task(callback(*args, **kwargs))
                cls._tasks.add(task)
                task.add_done_callback(cls._tasks.discard)
