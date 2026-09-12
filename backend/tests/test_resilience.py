import pytest
import asyncio
from app.core.resilience import with_retry, CircuitBreaker

@pytest.mark.asyncio
async def test_with_retry_success_first_try():
    async def my_func():
        return "success"

    res = await with_retry(my_func)
    assert res == "success"

@pytest.mark.asyncio
async def test_with_retry_success_after_fail():
    calls = 0
    async def my_func():
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ValueError("fail")
        return "success"

    res = await with_retry(my_func, max_attempts=3)
    assert res == "success"
    assert calls == 2

@pytest.mark.asyncio
async def test_with_retry_failure():
    calls = 0
    async def my_func():
        nonlocal calls
        calls += 1
        raise ValueError("fail")

    with pytest.raises(ValueError):
        await with_retry(my_func, max_attempts=2)
    assert calls == 2

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    calls = 0
    async def my_func():
        nonlocal calls
        calls += 1
        raise ValueError("fail")

    async def fallback(*args, **kwargs):
        return "fallback"

    # 1st fail
    res = await cb.call(my_func, fallback_func=fallback)
    assert res == "fallback"
    assert cb.state == "CLOSED"

    # 2nd fail -> OPEN
    res = await cb.call(my_func, fallback_func=fallback)
    assert res == "fallback"
    assert cb.state == "OPEN"

    # 3rd call immediately -> still OPEN, calls fallback, func not called
    calls_before = calls
    res = await cb.call(my_func, fallback_func=fallback)
    assert res == "fallback"
    assert cb.state == "OPEN"
    assert calls == calls_before

    # wait -> HALF-OPEN
    await asyncio.sleep(0.15)

    async def success_func():
        return "success"

    res = await cb.call(success_func, fallback_func=fallback)
    assert res == "success"
    assert cb.state == "CLOSED"
