import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Needs to be mocked before importing IntegrationService
import sys

# Fake out external dependencies we don't want to actually load for this test
sys.modules['cloudinary'] = MagicMock()
sys.modules['cloudinary.uploader'] = MagicMock()
sys.modules['algoliasearch'] = MagicMock()
sys.modules['algoliasearch.search_client'] = MagicMock()
sys.modules['sendgrid'] = MagicMock()
sys.modules['sendgrid.helpers.mail'] = MagicMock()
sys.modules['stream_chat'] = MagicMock()

from app.api.integrations import IntegrationService
from app.core.resilience import circuit_breaker_states, CircuitBreakerOpenException

@pytest.fixture(autouse=True)
def reset_circuit_breaker_state():
    """Reset the circuit breaker states before each test to ensure isolation."""
    circuit_breaker_states.clear()
    yield

@pytest.mark.asyncio
async def test_retry_on_failure():
    service = IntegrationService()

    # Mock the internal object to fail twice, then succeed
    call_count = {"count": 0}

    async def mock_upload(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise Exception("Transient failure")
        return {"secure_url": "http://example.com/report.pdf"}

    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.side_effect = mock_upload

        result = await service.upload_report_to_cloudinary(b"test data", "123")

        assert call_count["count"] == 3
        assert result == "http://example.com/report.pdf"

@pytest.mark.asyncio
async def test_circuit_breaker_trips():
    service = IntegrationService()

    async def mock_upload_fail(*args, **kwargs):
        raise Exception("Persistent failure")

    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.side_effect = mock_upload_fail

        # It should fail 3 times (due to retry) and then raise the exception on the first call
        with pytest.raises(Exception, match="Persistent failure"):
            await service.upload_report_to_cloudinary(b"test data", "123")

        # The first call actually consumes 3 attempts because of the inner `@with_retry`.
        # However, the breaker counts exceptions bubbled up *after* retries.
        # Wait, the circuit breaker gets an exception after retries. So one failure.
        # Let's call it 2 more times to trip the breaker.
        with pytest.raises(Exception, match="Persistent failure"):
            await service.upload_report_to_cloudinary(b"test data", "123")

        with pytest.raises(Exception, match="Persistent failure"):
            await service.upload_report_to_cloudinary(b"test data", "123")

        # Now the circuit breaker should be open
        with pytest.raises(CircuitBreakerOpenException, match="Circuit breaker is OPEN"):
            await service.upload_report_to_cloudinary(b"test data", "123")
