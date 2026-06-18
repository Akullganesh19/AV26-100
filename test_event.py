import asyncio
from app.services.event_bus import event_bus

async def listener(msg):
    print("Received:", msg)

event_bus.subscribe("test", listener)

async def main():
    await event_bus.publish("test", "Hello World")

asyncio.run(main())
