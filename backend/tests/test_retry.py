import pytest
from unittest.mock import AsyncMock, patch
from app.core.retry import with_retry

@pytest.mark.asyncio
async def test_with_retry_success_first_try():
    mock_func = AsyncMock(return_value="success")
    result = await with_retry(mock_func, "arg1", kwarg1="val1", max_attempts=3, base_delay=0)
    assert result == "success"
    mock_func.assert_called_once_with("arg1", kwarg1="val1")

@pytest.mark.asyncio
async def test_with_retry_success_after_failure():
    mock_func = AsyncMock(side_effect=[ValueError("fail"), "success"])
    result = await with_retry(mock_func, max_attempts=3, base_delay=0)
    assert result == "success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_with_retry_failure_with_raise():
    mock_func = AsyncMock(side_effect=ValueError("fail"))
    with pytest.raises(ValueError, match="fail"):
        await with_retry(mock_func, max_attempts=3, base_delay=0, raise_on_failure=True)
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_with_retry_failure_with_fallback():
    mock_func = AsyncMock(side_effect=ValueError("fail"))
    result = await with_retry(
        mock_func,
        max_attempts=3,
        base_delay=0,
        raise_on_failure=False,
        fallback="default_val"
    )
    assert result == "default_val"
    assert mock_func.call_count == 3
