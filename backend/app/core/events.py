import logging
from typing import Callable, Dict, List, Any
import asyncio

logger = logging.getLogger(__name__)

class EventBus:
    """
    A lightweight in-memory event bus for loosely coupled cross-system communication.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Register a callback for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    async def publish(self, event_type: str, payload: Any = None) -> None:
        """Publish an event asynchronously to all registered subscribers."""
        if event_type not in self._subscribers:
            return

        logger.info(f"EventBus published: {event_type}")

        # Dispatch to all subscribers
        for callback in self._subscribers[event_type]:
            try:
                # If callback is a coroutine, await it, else call it synchronously
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(payload))
                else:
                    callback(payload)
            except Exception as e:
                logger.error(f"Error in event subscriber for {event_type}: {str(e)}", exc_info=True)

# Singleton instance
event_bus = EventBus()
