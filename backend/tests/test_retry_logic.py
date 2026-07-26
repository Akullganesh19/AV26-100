import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.core.utils import with_retry

@pytest.mark.asyncio
async def test_with_retry_success_first_try():
    mock_func = MagicMock(return_value="success")
    async def async_mock_func(*args, **kwargs):
        return mock_func(*args, **kwargs)

    result = await with_retry(async_mock_func, max_attempts=3)
    assert result == "success"
    assert mock_func.call_count == 1

@pytest.mark.asyncio
async def test_with_retry_success_after_failure():
    mock_func = MagicMock(side_effect=[Exception("fail"), "success"])
    async def async_mock_func(*args, **kwargs):
        return mock_func(*args, **kwargs)

    with patch("asyncio.sleep", return_value=None):
        result = await with_retry(async_mock_func, max_attempts=3)

    assert result == "success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_with_retry_fails_all_attempts():
    mock_func = MagicMock(side_effect=Exception("fail"))
    async def async_mock_func(*args, **kwargs):
        return mock_func(*args, **kwargs)

    with patch("asyncio.sleep", return_value=None):
        with pytest.raises(Exception, match="fail"):
            await with_retry(async_mock_func, max_attempts=3)

    assert mock_func.call_count == 3
