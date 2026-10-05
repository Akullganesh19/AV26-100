import pytest
import asyncio
from app.core.resilience import with_retry, fire_and_forget, _background_tasks

@pytest.mark.asyncio
async def test_with_retry_success_first_try():
    calls = 0
    @with_retry(max_attempts=3)
    async def always_succeeds():
        nonlocal calls
        calls += 1
        return "success"

    res = await always_succeeds()
    assert res == "success"
    assert calls == 1

@pytest.mark.asyncio
async def test_with_retry_success_second_try():
    calls = 0
    @with_retry(max_attempts=3, base_delay=0.01)
    async def succeeds_second_time():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ValueError("fail")
        return "success"

    res = await succeeds_second_time()
    assert res == "success"
    assert calls == 2

@pytest.mark.asyncio
async def test_with_retry_exhaustion():
    calls = 0
    @with_retry(max_attempts=3, base_delay=0.01)
    async def always_fails():
        nonlocal calls
        calls += 1
        raise ValueError("fail")

    with pytest.raises(ValueError, match="fail"):
        await always_fails()
    assert calls == 3

@pytest.mark.asyncio
async def test_fire_and_forget():
    done = False
    async def my_task():
        nonlocal done
        await asyncio.sleep(0.01)
        done = True

    task = fire_and_forget(my_task(), name="test_task")
    assert task in _background_tasks
    await task
    assert done
    assert task not in _background_tasks
