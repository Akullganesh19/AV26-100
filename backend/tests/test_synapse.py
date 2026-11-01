import pytest
import asyncio
from app.connections.synapse_bridge import EventBus, event_bus

@pytest.mark.asyncio
async def test_event_bus():
    bus = EventBus()
    received = []

    async def listener(**kwargs):
        received.append(kwargs.get("val"))

    bus.subscribe("test.event", listener)
    await bus.publish("test.event", val=42)

    assert received == [42]
