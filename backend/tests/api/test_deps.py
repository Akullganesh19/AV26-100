import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    mock_db = AsyncMock()
    token = "test_token"
    public_key = "test_key"

    with patch("jose.jwt.get_unverified_claims") as mock_unverified:
        mock_unverified.return_value = {"jti": "123"}

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.get.return_value = b"true"
            mock_redis.return_value = mock_redis_instance

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=mock_db, token=token, public_key=public_key)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token has been revoked"


@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    mock_db = AsyncMock()
    token = "test_token"
    public_key = "test_key"

    with patch("jose.jwt.get_unverified_claims") as mock_unverified:
        mock_unverified.return_value = {"jti": "123"}

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.get.return_value = b"true"
            mock_redis.return_value = mock_redis_instance

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=mock_db, token=token, public_key=public_key)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token has been revoked"
