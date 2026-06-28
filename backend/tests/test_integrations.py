import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.fixture(autouse=True)
def mock_settings():
    with patch("app.api.integrations.settings.ALGOLIA_API_KEY", "dummy"), \
         patch("app.api.integrations.settings.SENDGRID_API_KEY", "dummy"):
        yield

@pytest.fixture
def mock_integration_service():
    with patch("app.api.integrations.SearchClientSync") as mock_algolia, \
         patch("app.api.integrations.SendGridAPIClient") as mock_sg:

        # we need to re-import it so the __init__ is called with the patched classes
        from app.api.integrations import IntegrationService

        mock_index = MagicMock()
        # Mock hasattr checks in sync_district_to_algolia
        mock_index.save_objects = MagicMock()
        mock_algolia.return_value = mock_index

        service = IntegrationService()
        service.index = mock_index
        service.sg = mock_sg.return_value

        yield service, mock_index, mock_sg.return_value

@pytest.mark.asyncio
async def test_algolia_sync_retries(mock_integration_service):
    service, mock_index, _ = mock_integration_service

    async def mock_to_thread(func, *args):
        return func(*args)

    with patch("app.api.integrations.asyncio.to_thread", new=mock_to_thread):
        mock_index.save_objects = MagicMock(side_effect=[Exception("transient"), {"objectID": "123"}])
        # Need to explicitly set save_object to raise AttributeError so it falls back to save_objects,
        # or we could just set save_object side effect
        del mock_index.save_object

        await service.sync_district_to_algolia({"id": "123", "name": "Test"})
        assert mock_index.save_objects.call_count == 2

@pytest.mark.asyncio
async def test_sendgrid_idempotency(mock_integration_service):
    service, _, mock_sg = mock_integration_service

    async def mock_to_thread(func, *args):
        return func(*args)

    with patch("app.api.integrations.asyncio.to_thread", new=mock_to_thread):
        mock_sg.send = MagicMock(return_value=True)

        await service.send_health_alert_email("test@test.com", "Test", "Malaria", 90.0, idempotency_key="alert-1")
        assert mock_sg.send.call_count == 1
