import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_does_not_swallow_exception(mocker):
    # Mock JWT parsing and redis check
    mocker.patch("jose.jwt.get_unverified_claims", return_value={"jti": "mock_jti"})
    mock_redis = mocker.patch("redis.asyncio.from_url")
    mock_redis_instance = AsyncMock()
    # Mock redis to return true for revoked token check
    mock_redis_instance.get.return_value = b"1"
    mock_redis.return_value = mock_redis_instance

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db=AsyncMock(), token="mock_token", public_key="mock_key")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"
