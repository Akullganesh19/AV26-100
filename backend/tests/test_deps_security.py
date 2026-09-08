import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from jose import jwt
import redis.asyncio as redis

from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_revoked_token_is_not_swallowed():
    with patch("app.api.deps.jwt.get_unverified_claims") as mock_claims, \
         patch("redis.asyncio.from_url") as mock_redis:

        mock_claims.return_value = {"jti": "bad_token"}

        mock_r = AsyncMock()
        mock_r.get.return_value = b"1"
        mock_redis.return_value = mock_r

        db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=db, token="fake_token", public_key="fake_key")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has been revoked"
