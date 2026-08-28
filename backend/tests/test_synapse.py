import pytest
import asyncio
from app.core.event_bus import event_bus

@pytest.mark.asyncio
async def test_event_bus():
    called = False

    async def mock_handler(data):
        nonlocal called
        called = True
        assert data == "test_payload"

    event_bus.subscribe("test.event", mock_handler)
    event_bus.publish("test.event", "test_payload")

    # Give background tasks a moment to execute
    await asyncio.sleep(0.1)

    assert called
