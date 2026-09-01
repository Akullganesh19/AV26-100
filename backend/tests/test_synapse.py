import pytest
import asyncio
from app.core.events import EventBus

@pytest.mark.asyncio
async def test_event_bus():
    received = []

    async def dummy_callback(alert_id, district_id, risk_score, disease):
        received.append((alert_id, district_id, risk_score, disease))

    EventBus.subscribe("test.alert.created", dummy_callback)
    EventBus.publish("test.alert.created", "a1", "d1", 0.95, "heart")

    # Wait for tasks to complete
    await asyncio.sleep(0.1)

    assert len(received) == 1
    assert received[0] == ("a1", "d1", 0.95, "heart")
