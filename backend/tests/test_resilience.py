import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.core.resilience import with_retry, with_circuit_breaker, CircuitBreakerOpenException

@pytest.mark.asyncio
async def test_with_retry_success():
    mock_func = AsyncMock(return_value="success")
    mock_func.__qualname__ = "mock_func"
    decorated_func = with_retry(max_retries=3, idempotent=True)(mock_func)

    result = await decorated_func()
    assert result == "success"
    mock_func.assert_awaited_once()

@pytest.mark.asyncio
async def test_with_retry_failure_then_success():
    mock_func = AsyncMock(side_effect=[Exception("fail 1"), Exception("fail 2"), "success"])
    mock_func.__qualname__ = "mock_func"
    decorated_func = with_retry(max_retries=3, base_delay=0.01, max_delay=0.05, idempotent=True)(mock_func)

    result = await decorated_func()
    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_with_retry_max_retries_exhausted():
    mock_func = AsyncMock(side_effect=Exception("persistent fail"))
    mock_func.__qualname__ = "mock_func"
    decorated_func = with_retry(max_retries=3, base_delay=0.01, max_delay=0.05, idempotent=True)(mock_func)

    with pytest.raises(Exception, match="persistent fail"):
        await decorated_func()
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_circuit_breaker_trips():
    mock_func = AsyncMock(side_effect=Exception("fail"))
    mock_func.__qualname__ = "mock_func"
    decorated_func = with_circuit_breaker(failure_threshold=2)(mock_func)

    with pytest.raises(Exception):
        await decorated_func()
    with pytest.raises(Exception):
        await decorated_func()

    with pytest.raises(CircuitBreakerOpenException, match="Circuit breaker .* is OPEN"):
        await decorated_func()

    assert mock_func.call_count == 2
