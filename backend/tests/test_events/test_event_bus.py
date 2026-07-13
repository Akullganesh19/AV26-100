import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.core.events import EventBus

@pytest.mark.asyncio
async def test_event_bus_sync_subscriber():
    bus = EventBus()
    mock_callback = MagicMock()

    bus.on("test.sync", mock_callback)
    bus.emit("test.sync", "data", value=1)

    mock_callback.assert_called_once_with("data", value=1)

@pytest.mark.asyncio
async def test_event_bus_async_subscriber():
    bus = EventBus()
    mock_callback = AsyncMock()

    bus.on("test.async", mock_callback)
    bus.emit("test.async", "data", value=2)

    # Need to wait for background tasks to complete
    await asyncio.gather(*bus._background_tasks)

    mock_callback.assert_called_once_with("data", value=2)
