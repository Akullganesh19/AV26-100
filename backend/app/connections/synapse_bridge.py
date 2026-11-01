import asyncio
from typing import Callable, Dict, List, Any

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    async def publish(self, event_name: str, **kwargs):
        if event_name in self._subscribers:
            tasks = [callback(**kwargs) for callback in self._subscribers[event_name]]
            await asyncio.gather(*tasks)

event_bus = EventBus()
