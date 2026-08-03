import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.fixture
def mock_settings():
    with patch("app.core.config.settings") as mock:
        mock.ALGOLIA_APP_ID = "test"
        mock.ALGOLIA_API_KEY = "test"
        mock.SENDGRID_API_KEY = "test"
        mock.STREAM_API_KEY = "test"
        mock.STREAM_API_SECRET = "test"
        yield mock

@pytest.fixture
def integration_service(mock_settings):
    # Mock the initialization dependencies so they don't try to connect to real services
    with patch("app.api.integrations.SearchClient.create"), \
         patch("app.api.integrations.SendGridAPIClient"), \
         patch("app.api.integrations.StreamChat"), \
         patch("app.api.integrations.settings", mock_settings):
        from app.api.integrations import IntegrationService
        return IntegrationService()

@pytest.mark.asyncio
async def test_upload_report_to_cloudinary_graceful_degradation(integration_service):
    # Mock with_retry to raise an exception, simulating ultimate failure
    with patch("app.api.integrations.with_retry", new_callable=AsyncMock) as mock_with_retry:
        mock_with_retry.side_effect = Exception("Cloudinary ultimate failure")

        result = await integration_service.upload_report_to_cloudinary(b"dummy bytes", "123")

        # It should return None on failure (graceful degradation) instead of crashing
        assert result is None

@pytest.mark.asyncio
async def test_sync_district_to_algolia_graceful_degradation(integration_service):
    with patch("app.api.integrations.with_retry", new_callable=AsyncMock) as mock_with_retry:
        mock_with_retry.side_effect = Exception("Algolia ultimate failure")

        # Should not raise exception
        result = await integration_service.sync_district_to_algolia({"id": "123"})

        assert result is None

@pytest.mark.asyncio
async def test_send_health_alert_email_graceful_degradation(integration_service):
    with patch("app.api.integrations.asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.side_effect = Exception("Sendgrid ultimate failure")

        # Should not raise exception
        result = await integration_service.send_health_alert_email("test@example.com", "District 9", "Flu", 0.9)

        assert result is None

@pytest.mark.asyncio
async def test_with_retry_utility():
    from app.core.utils import with_retry

    # Track number of calls
    calls = 0
    def failing_func():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise Exception("Temporary failure")
        return "Success"

    result = await with_retry(failing_func, max_attempts=3, base_delay=0.01)

    assert result == "Success"
    assert calls == 3

@pytest.mark.asyncio
async def test_with_retry_ultimate_failure():
    from app.core.utils import with_retry

    calls = 0
    def constantly_failing_func():
        nonlocal calls
        calls += 1
        raise Exception("Permanent failure")

    with pytest.raises(Exception, match="Permanent failure"):
        await with_retry(constantly_failing_func, max_attempts=2, base_delay=0.01)

    assert calls == 2
