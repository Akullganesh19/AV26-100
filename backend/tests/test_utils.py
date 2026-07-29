import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.core.utils import with_retry

@pytest.mark.asyncio
async def test_with_retry_success():
    mock_func = AsyncMock(return_value="success")
    result = await with_retry(mock_func, "arg1", kwarg1="val1", max_attempts=3)
    assert result == "success"
    mock_func.assert_called_once_with("arg1", kwarg1="val1")

@pytest.mark.asyncio
async def test_with_retry_eventual_success():
    mock_func = AsyncMock(side_effect=[Exception("fail 1"), Exception("fail 2"), "success"])

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await with_retry(mock_func, max_attempts=3)
        assert result == "success"
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2

        # Verify exponential backoff
        mock_sleep.assert_any_call(0.1) # attempt 1
        mock_sleep.assert_any_call(0.2) # attempt 2

@pytest.mark.asyncio
async def test_with_retry_max_attempts_exceeded():
    mock_func = AsyncMock(side_effect=Exception("persistent fail"))

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(Exception, match="persistent fail"):
            await with_retry(mock_func, max_attempts=3)

        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2
