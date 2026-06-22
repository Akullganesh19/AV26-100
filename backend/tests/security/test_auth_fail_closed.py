import pytest
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_auth_fails_closed_on_redis_error():
    """
    Ensures that if the Redis instance tracking revoked tokens is down,
    we fail closed (HTTP 500) rather than failing open and allowing potentially
    revoked tokens.
    """
    mock_db = AsyncMock()
    # A valid mock token that would otherwise pass parsing
    # Use a token generated with jwt.encode so that the formatting and padding are perfectly valid
    import jwt
    token = jwt.encode({"sub": "123", "jti": "abc"}, "secret", algorithm="HS256")
    public_key = "dummy_key"

    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        # Simulate a connection or timeout error from Redis
        mock_redis.get.side_effect = Exception("Redis connection refused")
        mock_from_url.return_value = mock_redis

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, token=token, public_key=public_key)

        assert exc_info.value.status_code == 500
        assert "Internal server error" in exc_info.value.detail

@pytest.mark.asyncio
async def test_auth_fails_on_revoked_token():
    """
    Ensures that if a token's JTI is in Redis as revoked,
    we correctly raise a 401 Unauthorized instead of bypassing it.
    """
    mock_db = AsyncMock()
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiamRpIjoiYWJjIn0.dummy"
    public_key = "dummy_key"

    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        # Simulate Redis confirming the token is revoked
        mock_redis.get.return_value = b"1"
        mock_from_url.return_value = mock_redis

        with pytest.raises(HTTPException) as exc_info:
            # We must mock jwt.decode so it returns a payload with a 'jti'
            with patch("jwt.decode", return_value={"sub": "123", "jti": "abc"}):
                await get_current_user(db=mock_db, token=token, public_key=public_key)

        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail
