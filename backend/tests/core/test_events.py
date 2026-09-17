import pytest
import asyncio
from unittest.mock import AsyncMock
from app.core.events import EventBus

@pytest.mark.asyncio
async def test_event_bus():
    bus = EventBus()
    mock_listener = AsyncMock()
    bus.subscribe("test.event", mock_listener)
    bus.publish("test.event", "arg1", kwarg1="val1")
    await asyncio.sleep(0.1) # Yield to event loop to allow task to run
    mock_listener.assert_called_once_with("arg1", kwarg1="val1")
