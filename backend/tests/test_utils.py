import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.core.utils import with_retry

@pytest.mark.asyncio
async def test_with_retry_success_first_try():
    mock_func = AsyncMock(return_value="success")
    result = await with_retry(mock_func, "arg1", kwarg1="test")
    assert result == "success"
    mock_func.assert_called_once_with("arg1", kwarg1="test")

@pytest.mark.asyncio
async def test_with_retry_success_after_failures():
    mock_func = AsyncMock(side_effect=[Exception("fail 1"), Exception("fail 2"), "success"])
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await with_retry(mock_func, max_attempts=3)
        assert result == "success"
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)

@pytest.mark.asyncio
async def test_with_retry_ultimate_failure():
    mock_func = AsyncMock(side_effect=Exception("persistent failure"))
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(Exception, match="persistent failure"):
            await with_retry(mock_func, max_attempts=3)
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2
