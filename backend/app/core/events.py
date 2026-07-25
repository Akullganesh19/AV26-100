import asyncio
import logging
from collections import defaultdict
from typing import Callable, Dict, List, Any, Awaitable

logger = logging.getLogger(__name__)

# Strong references for background tasks to prevent premature garbage collection
_background_tasks = set()

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[..., Awaitable[None]]]] = defaultdict(list)

    def on(self, event_type: str):
        def decorator(func: Callable[..., Awaitable[None]]):
            self._subscribers[event_type].append(func)
            return func
        return decorator

    async def emit(self, event_type: str, **kwargs: Any):
        logger.info(f"EventBus emitting: {event_type}")
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            # We don't await handler here because we want fire-and-forget
            # Wrap the coroutine in a task
            task = asyncio.create_task(handler(**kwargs))
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)

event_bus = EventBus()
