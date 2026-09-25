import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from jose import jwt
from app.api.deps import get_current_user

@pytest.mark.asyncio
@patch('redis.asyncio.from_url')
async def test_revoked_token_fails_401(mock_from_url):
    """Test that a revoked token correctly raises a 401 Unauthorized exception."""
    # Mock Redis client
    mock_redis = AsyncMock()
    mock_from_url.return_value = mock_redis

    # Mock r.get to return True -> token is revoked
    mock_redis.get.return_value = b'1'

    token = jwt.encode({"sub": "user_123", "jti": "jti_456"}, "secret", algorithm="HS256")
    db = AsyncMock()
    public_key = "secret"

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(db=db, token=token, public_key=public_key)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token has been revoked"

@pytest.mark.asyncio
@patch('redis.asyncio.from_url')
async def test_redis_failure_fails_closed_503(mock_from_url):
    """Test that if Redis is unreachable, the system fails closed with a 503."""
    # Mock Redis client
    mock_redis = AsyncMock()
    mock_from_url.return_value = mock_redis

    # Mock r.get to raise an exception simulating Redis being down
    mock_redis.get.side_effect = Exception("Redis connection refused")

    token = jwt.encode({"sub": "user_123", "jti": "jti_456"}, "secret", algorithm="HS256")
    db = AsyncMock()
    public_key = "secret"

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(db=db, token=token, public_key=public_key)

    assert excinfo.value.status_code == 503
    assert excinfo.value.detail == "Security infrastructure unavailable. Cannot verify token revocation status."
