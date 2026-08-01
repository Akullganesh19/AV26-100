import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from app.core.utils import with_retry

@pytest.mark.asyncio
async def test_with_retry_success_first_try():
    mock_func = AsyncMock(return_value="success")
    result = await with_retry(mock_func, "arg1", kwarg1="val1", max_attempts=3, base_delay=0.01)

    assert result == "success"
    mock_func.assert_awaited_once_with("arg1", kwarg1="val1")

@pytest.mark.asyncio
async def test_with_retry_success_after_failure():
    mock_func = AsyncMock(side_effect=[Exception("failure 1"), "success"])
    result = await with_retry(mock_func, "arg1", max_attempts=3, base_delay=0.01)

    assert result == "success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_with_retry_exhaust_retries():
    mock_func = AsyncMock(side_effect=Exception("permanent failure"))

    with pytest.raises(Exception, match="permanent failure"):
        await with_retry(mock_func, max_attempts=3, base_delay=0.01)

    assert mock_func.call_count == 3
