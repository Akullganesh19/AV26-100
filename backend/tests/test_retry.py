import pytest
from unittest.mock import AsyncMock
from app.core.retry import with_retry

@pytest.mark.asyncio
async def test_with_retry_success():
    """Test that with_retry returns the correct result on success."""
    mock_func = AsyncMock(return_value="success")
    result = await with_retry(mock_func, "arg1", kwarg1="kwarg1")

    assert result == "success"
    mock_func.assert_called_once_with("arg1", kwarg1="kwarg1")

@pytest.mark.asyncio
async def test_with_retry_success_after_failure():
    """Test that with_retry succeeds after an initial failure."""
    mock_func = AsyncMock(side_effect=[Exception("First attempt failed"), "success"])

    result = await with_retry(mock_func, max_attempts=3)

    assert result == "success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_with_retry_ultimate_failure():
    """Test that with_retry raises the exception after max_attempts failures."""
    mock_func = AsyncMock(side_effect=Exception("Always fails"))

    with pytest.raises(Exception, match="Always fails"):
        await with_retry(mock_func, max_attempts=3)

    assert mock_func.call_count == 3
