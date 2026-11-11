import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from app.api.deps import get_current_user
from jose import jwt

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b'1'

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        token = jwt.encode({"jti": "revoked-123", "sub": "user_1"}, "secret", algorithm="HS256")

        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(db=AsyncMock(), token=token, public_key="dummy_key")

        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Token has been revoked"
