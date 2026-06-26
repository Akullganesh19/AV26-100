import sys
import os
sys.path.insert(0, os.path.abspath('backend'))
import asyncio
from app.core.resilience import with_retry, with_circuit_breaker, with_idempotency_guard

calls = 0

@with_retry(max_attempts=3, base_delay=0.1)
async def flaky_func():
    global calls
    calls += 1
    if calls < 3:
        raise ValueError("Oops")
    return "success"

async def test_retry():
    res = await flaky_func()
    print("Flaky result:", res)
    assert calls == 3

asyncio.run(test_retry())
