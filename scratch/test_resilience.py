import asyncio
import time
import pytest
import logging
from app.core.resilience import with_retry, with_circuit_breaker, CircuitBreakerOpenException

logging.basicConfig(level=logging.INFO)

class DummyService:
    def __init__(self):
        self.calls = 0

    @with_circuit_breaker(failure_threshold=2, recovery_timeout=1.0)
    @with_retry(max_attempts=3, base_delay=0.1, max_delay=0.5)
    async def flappy_method(self, fail_times):
        self.calls += 1
        if self.calls <= fail_times:
            raise ValueError("Transient error")
        return "success"

@pytest.mark.asyncio
async def test_resilience():
    service = DummyService()

    # Test retry: fail 2 times, succeed on 3rd
    res = await service.flappy_method(fail_times=2)
    assert res == "success"
    assert service.calls == 3

    # Test circuit breaker: fail completely
    service.calls = 0
    try:
        await service.flappy_method(fail_times=10)
    except ValueError:
        pass

    try:
        await service.flappy_method(fail_times=10)
    except ValueError:
        pass

    # Circuit should be open now
    try:
        await service.flappy_method(fail_times=10)
        assert False, "Should have raised exception"
    except Exception as e:
        assert "Circuit breaker OPEN" in str(e)

    # Wait for recovery timeout
    await asyncio.sleep(1.1)

    # Should be half open, we will make it fail
    try:
        await service.flappy_method(fail_times=10)
    except ValueError:
        pass

    # Next call should be open again
    try:
        await service.flappy_method(fail_times=10)
        assert False, "Should have raised exception"
    except Exception as e:
        assert "Circuit breaker OPEN" in str(e)

    # Wait for recovery again
    await asyncio.sleep(1.1)

    # Make it succeed
    service.calls = 0
    res = await service.flappy_method(fail_times=0)
    assert res == "success"
