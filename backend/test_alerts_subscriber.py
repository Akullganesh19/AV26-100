import asyncio
from app.core.events import event_bus
from app.subscribers import init_subscribers

async def main():
    init_subscribers()
    # Mocking out the DB session since postgres isn't running
    from app.subscribers import alerts_subscriber

    original_handle = alerts_subscriber.handle_alert_triggered
    async def mock_handle(*args, **kwargs):
        print(f"Mock handler received: {args} {kwargs}")

    alerts_subscriber.handle_alert_triggered = mock_handle

    # Unsubscribe the old one and add the mocked one
    event_bus.subscribers["alert.triggered"] = [mock_handle]

    event_bus.publish(
        "alert.triggered",
        alert_id="test_alert_id",
        district_id="test_district_id",
        disease="test_disease",
        risk_score=0.9,
        district_name="Test District"
    )
    await asyncio.sleep(0.5) # wait for async handlers
    print("Test published successfully")

if __name__ == "__main__":
    asyncio.run(main())
