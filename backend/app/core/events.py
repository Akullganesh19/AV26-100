import asyncio
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    A simple in-memory publish-subscribe event bus to facilitate
    cross-system communication without tight coupling.
    """

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        logger.info(f"EventBus: Registered listener for {event_type}")

    async def publish(self, event_type: str, *args, **kwargs):
        if event_type not in self._listeners:
            return

        logger.debug(f"EventBus: Publishing {event_type}")

        # Run all listeners for this event concurrently
        tasks = []
        for callback in self._listeners[event_type]:
            if asyncio.iscoroutinefunction(callback):
                tasks.append(asyncio.create_task(callback(*args, **kwargs)))
            else:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Error in sync event listener for {event_type}: {str(e)}",
                        exc_info=True,
                    )

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(
                        f"Error in async event listener for {event_type}: {str(result)}"
                    )


# Global event bus instance
event_bus = EventBus()
