import pytest
import asyncio
from app.core.resilience import with_retry

@pytest.mark.asyncio
async def test_retry_success():
    attempts = 0
    async def dummy_func():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Transient error")
        return "Success"

    res = await with_retry(dummy_func, max_attempts=3, base_delay=0.1)
    assert res == "Success"
    assert attempts == 2

@pytest.mark.asyncio
async def test_retry_failure():
    attempts = 0
    async def dummy_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Permanent error")

    with pytest.raises(ValueError, match="Permanent error"):
        await with_retry(dummy_func, max_attempts=2, base_delay=0.1)

    assert attempts == 2
