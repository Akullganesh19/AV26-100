import asyncio
from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)

    def publish(self, event_name: str, *args, **kwargs):
        if event_name not in self.subscribers:
            return
        for callback in self.subscribers[event_name]:
            if asyncio.iscoroutinefunction(callback):
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(callback(*args, **kwargs))
                except RuntimeError:
                    asyncio.run(callback(*args, **kwargs))
            else:
                callback(*args, **kwargs)

bus = EventBus()

async def my_sub(msg):
    print(f"Sub got: {msg}")

bus.subscribe("test", my_sub)

async def main():
    bus.publish("test", "hello")
    await asyncio.sleep(0.1)

asyncio.run(main())
