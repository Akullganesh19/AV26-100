import pytest
import asyncio
from app.core.resilience import with_retry, CircuitBreaker

@pytest.mark.asyncio
async def test_with_retry_success():
    count = 0
    @with_retry(max_attempts=3, base_delay=0.01)
    async def flaky():
        nonlocal count
        count += 1
        if count < 3:
            raise ValueError("Flaky error")
        return "Success"

    res = await flaky()
    assert res == "Success"
    assert count == 3

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    async def failing_target(*args, **kwargs):
        raise ValueError("Target failed")

    async def success_target(*args, **kwargs):
        return "Success"

    async def fallback(*args, **kwargs):
        return "Fallback"

    # Attempt 1: fails
    res1 = await cb(failing_target, fallback)
    assert res1 == "Fallback"
    assert cb.state == "CLOSED"

    # Attempt 2: fails, trips breaker
    res2 = await cb(failing_target, fallback)
    assert res2 == "Fallback"
    assert cb.state == "OPEN"

    # Attempt 3: fails fast
    res3 = await cb(success_target, fallback)
    assert res3 == "Fallback"

    # Wait for recovery
    await asyncio.sleep(0.15)

    # Attempt 4: half-open, success, closes breaker
    res4 = await cb(success_target, fallback)
    assert res4 == "Success"
    assert cb.state == "CLOSED"
