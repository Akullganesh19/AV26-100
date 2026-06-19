import pytest
import asyncio
import time
from app.core.resilience import with_retry, with_circuit_breaker, CircuitBreakerOpenException

@pytest.mark.asyncio
async def test_retry_success_after_failure():
    attempts = 0

    @with_retry(max_attempts=3, initial_backoff=0.01)
    async def flaky_function():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Failed")
        return "Success"

    result = await flaky_function()
    assert result == "Success"
    assert attempts == 3

@pytest.mark.asyncio
async def test_retry_exhaustion():
    attempts = 0

    @with_retry(max_attempts=2, initial_backoff=0.01)
    async def failing_function():
        nonlocal attempts
        attempts += 1
        raise ValueError("Failed")

    with pytest.raises(ValueError, match="Failed"):
        await failing_function()
    assert attempts == 2

@pytest.mark.asyncio
async def test_circuit_breaker_fails_fast():
    @with_circuit_breaker(failure_threshold=2, recovery_timeout=1.0)
    async def failing_function():
        raise ValueError("Failed")

    with pytest.raises(ValueError):
        await failing_function()
    with pytest.raises(ValueError):
        await failing_function()

    # 3rd attempt should fail fast with CircuitBreakerOpenException
    with pytest.raises(CircuitBreakerOpenException):
        await failing_function()
