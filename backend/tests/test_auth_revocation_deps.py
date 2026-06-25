import pytest
import asyncio
import redis.exceptions
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock
from jose import jwt

from app.api.deps import get_current_user
import app.models  # trigger registry properly

class MockUser:
    def __init__(self, clerk_id, is_active):
        self.clerk_id = clerk_id
        self.is_active = is_active

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_fails_closed():
    """Test that a revoked token properly raises a 401 instead of being swallowed."""
    token = "fake.token.part"
    db = AsyncMock()

    with patch("jose.jwt.get_unverified_claims", return_value={"jti": "123", "sub": "user_id"}), \
         patch("redis.asyncio.from_url") as mock_redis, \
         patch("jose.jwt.decode", return_value={"sub": "user_id"}):

        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.return_value = b"1" # Simulating revoked token
        mock_redis.return_value = mock_redis_instance

        user = MockUser(clerk_id="user_id", is_active=True)
        db_result = MagicMock()
        db_result.scalar_one_or_none.return_value = user
        db.execute.return_value = db_result

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=db, token=token, public_key="fake_key")

        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()

@pytest.mark.asyncio
async def test_get_current_user_redis_error_fails_closed():
    """Test that if the Redis connection fails during revocation check, it fails closed (500) rather than failing open."""
    token = "fake.token.part"
    db = AsyncMock()

    with patch("jose.jwt.get_unverified_claims", return_value={"jti": "123", "sub": "user_id"}), \
         patch("redis.asyncio.from_url") as mock_redis, \
         patch("jose.jwt.decode", return_value={"sub": "user_id"}):

        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.side_effect = redis.exceptions.ConnectionError("Redis connection refused!")
        mock_redis.return_value = mock_redis_instance

        user = MockUser(clerk_id="user_id", is_active=True)
        db_result = MagicMock()
        db_result.scalar_one_or_none.return_value = user
        db.execute.return_value = db_result

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=db, token=token, public_key="fake_key")

        assert exc_info.value.status_code == 500
        assert "error" in exc_info.value.detail.lower()
