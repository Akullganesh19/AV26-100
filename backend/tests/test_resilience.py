import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.core.resilience import with_retry, CircuitBreaker

@pytest.mark.asyncio
async def test_with_retry_success_first_try():
    mock_func = AsyncMock(return_value="success")
    result = await with_retry(mock_func)
    assert result == "success"
    assert mock_func.call_count == 1

@pytest.mark.asyncio
async def test_with_retry_success_after_failure():
    mock_func = AsyncMock(side_effect=[Exception("fail"), "success"])
    result = await with_retry(mock_func, max_attempts=3)
    assert result == "success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_with_retry_failure():
    mock_func = AsyncMock(side_effect=Exception("fail"))
    with pytest.raises(Exception):
        await with_retry(mock_func, max_attempts=3)
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_circuit_breaker_success():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
    target_func = AsyncMock(return_value="target")
    fallback_func = AsyncMock(return_value="fallback")

    result = await cb.call(target_func, fallback_func)

    assert result == "target"
    assert target_func.call_count == 1
    assert fallback_func.call_count == 0

@pytest.mark.asyncio
async def test_circuit_breaker_trip():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
    target_func = AsyncMock(side_effect=Exception("fail"))
    fallback_func = AsyncMock(return_value="fallback")

    # 3 failures should trip it
    await cb.call(target_func, fallback_func)
    await cb.call(target_func, fallback_func)
    await cb.call(target_func, fallback_func)

    assert cb.state == "OPEN"
    assert target_func.call_count == 3
    assert fallback_func.call_count == 3

    # 4th call should use fallback immediately without calling target
    result = await cb.call(target_func, fallback_func)
    assert result == "fallback"
    assert cb.state == "OPEN"
    assert target_func.call_count == 3  # Target not called
    assert fallback_func.call_count == 4
