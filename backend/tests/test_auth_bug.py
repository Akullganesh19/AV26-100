import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.api.deps import get_current_user
from jose import jwt

@pytest.mark.asyncio
@patch("redis.asyncio.from_url")
async def test_get_current_user_revoked_token_throws(mock_redis_from_url):
    # Setup mock redis to return that token is revoked
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b"revoked"
    mock_redis_from_url.return_value = mock_redis

    # Create dummy token
    token = jwt.encode({"sub": "user123", "jti": "token123"}, "secret", algorithm="HS256")

    # Check that HTTPException is explicitly raised, not swallowed
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(db=AsyncMock(), token=token, public_key="dummy_key")

    assert excinfo.value.status_code == 401
    assert "Token has been revoked" in excinfo.value.detail
