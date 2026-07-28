import pytest
import asyncio
from unittest.mock import AsyncMock
from app.core.utils import with_retry

@pytest.mark.asyncio
async def test_with_retry_success():
    """Test that with_retry succeeds immediately if the function works."""
    mock_func = AsyncMock(return_value="success")
    result = await with_retry(mock_func, "arg1", kwarg1="kwarg1")
    assert result == "success"
    mock_func.assert_called_once_with("arg1", kwarg1="kwarg1")

@pytest.mark.asyncio
async def test_with_retry_eventual_success():
    """Test that with_retry retries and succeeds if it fails initially."""
    mock_func = AsyncMock(side_effect=[Exception("fail1"), Exception("fail2"), "success"])
    result = await with_retry(mock_func, max_attempts=3)
    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_with_retry_max_attempts_reached():
    """Test that with_retry raises the exception after max attempts."""
    mock_func = AsyncMock(side_effect=[Exception("fail1"), Exception("fail2")])
    with pytest.raises(Exception, match="fail2"):
        await with_retry(mock_func, max_attempts=2)
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_with_retry_async_func():
    """Test that with_retry works with async functions."""
    async def async_mock():
        return "async_success"
    result = await with_retry(async_mock)
    assert result == "async_success"
