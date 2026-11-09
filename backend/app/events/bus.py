import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._background_tasks = set()

    def on(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, **kwargs):
        if event_name not in self._listeners:
            return

        for callback in self._listeners[event_name]:
            if asyncio.iscoroutinefunction(callback):
                task = asyncio.create_task(self._safe_execute(callback, **kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"Error executing synchronous listener for {event_name}: {e}", exc_info=True)

    async def _safe_execute(self, callback: Callable, **kwargs):
        try:
            await callback(**kwargs)
        except Exception as e:
            logger.error(f"Error executing listener for: {e}", exc_info=True)

event_bus = EventBus()
