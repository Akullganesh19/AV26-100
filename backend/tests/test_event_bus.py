import pytest
import asyncio
from app.core.events import EventBus

@pytest.mark.asyncio
async def test_event_bus():
    bus = EventBus()
    called = False

    async def dummy_handler(val):
        nonlocal called
        called = val

    bus.subscribe("test.event", dummy_handler)
    bus.publish("test.event", val=True)

    # Allow background task to run
    await asyncio.sleep(0.1)

    assert called is True
