import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    mock_db = AsyncMock()
    token = "fake_token"
    public_key = "fake_key"

    with patch("app.api.deps.jwt.get_unverified_claims") as mock_get_unverified, \
         patch("redis.asyncio.from_url") as mock_redis_from_url:

        mock_get_unverified.return_value = {"jti": "fake_jti"}

        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.return_value = b"1"
        mock_redis_from_url.return_value = mock_redis_instance

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, token=token, public_key=public_key)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has been revoked"
