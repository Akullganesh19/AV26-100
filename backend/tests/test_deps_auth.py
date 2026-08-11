import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user
from jose import jwt
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_revoked_token_is_rejected():
    token = jwt.encode({"sub": "user123", "jti": "jti123"}, "secret", algorithm="HS256")

    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.return_value = b"revoked"
        mock_redis.return_value = mock_redis_instance

        try:
            await get_current_user(db=AsyncMock(), token=token, public_key="key")
        except HTTPException as e:
            if e.status_code == 401 and e.detail == "Token has been revoked":
                return # success
            raise e

        pytest.fail("HTTPException was not raised for revoked token")
