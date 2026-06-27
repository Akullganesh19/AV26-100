import pytest
import asyncio
import time
from unittest.mock import AsyncMock

from app.core.resilience import with_retry, with_circuit_breaker

@pytest.mark.asyncio
async def test_with_retry_success():
    mock_func = AsyncMock(return_value="success")
    decorated = with_retry(max_attempts=3, initial_backoff=0.01)(mock_func)

    result = await decorated()
    assert result == "success"
    assert mock_func.call_count == 1

@pytest.mark.asyncio
async def test_with_retry_recovers():
    mock_func = AsyncMock(side_effect=[ValueError("fail 1"), ValueError("fail 2"), "success"])
    decorated = with_retry(max_attempts=3, initial_backoff=0.01)(mock_func)

    result = await decorated()
    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_with_retry_fails_after_max_attempts():
    mock_func = AsyncMock(side_effect=ValueError("fail"))
    decorated = with_retry(max_attempts=3, initial_backoff=0.01)(mock_func)

    with pytest.raises(ValueError):
        await decorated()
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_with_circuit_breaker():
    mock_func = AsyncMock(side_effect=ValueError("fail"))

    # We must reset the state for each test if we reuse the function name,
    # but we generate a unique function name to avoid conflicts across tests
    async def unique_func_for_cb():
        return await mock_func()
    unique_func_for_cb.__name__ = "unique_func_for_cb"

    decorated = with_circuit_breaker(failure_threshold=2, recovery_timeout=0.1)(unique_func_for_cb)

    # Attempt 1: Fails
    with pytest.raises(ValueError):
        await decorated()

    # Attempt 2: Fails, threshold reached, state opens
    with pytest.raises(ValueError):
        await decorated()

    # Attempt 3: Fast fails with RuntimeError (Circuit Breaker OPEN)
    with pytest.raises(RuntimeError, match="Circuit breaker is OPEN"):
        await decorated()

    assert mock_func.call_count == 2

    # Wait for recovery timeout
    await asyncio.sleep(0.15)

    # Set mock to succeed now
    mock_func.side_effect = None
    mock_func.return_value = "success"

    # Attempt 4: Half-open, succeeds, closes circuit
    result = await decorated()
    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_retry_inside_circuit_breaker():
    mock_func = AsyncMock(side_effect=ValueError("fail"))

    async def cb_retry_func():
        return await mock_func()
    cb_retry_func.__name__ = "cb_retry_func"

    decorated = with_circuit_breaker(failure_threshold=2, recovery_timeout=0.1)(
        with_retry(max_attempts=2, initial_backoff=0.01)(cb_retry_func)
    )

    # The with_retry will swallow the first failure and retry,
    # then fail on the second attempt.
    # The circuit breaker sees this as ONE failure.
    with pytest.raises(ValueError):
        await decorated()
    assert mock_func.call_count == 2

    # Again, retry attempts twice.
    # The circuit breaker sees this as the SECOND failure, reaching threshold.
    with pytest.raises(ValueError):
        await decorated()
    assert mock_func.call_count == 4

    # Third time calling the decorated function, circuit breaker is OPEN, fast fails
    with pytest.raises(RuntimeError, match="Circuit breaker is OPEN"):
        await decorated()

    assert mock_func.call_count == 4
