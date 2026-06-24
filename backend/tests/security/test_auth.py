import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
import jwt

from app.api.deps import get_current_user
from app.core.config import settings

@pytest.mark.asyncio
async def test_redis_revocation_fail_closed():
    """Test that authentication fails closed (HTTP 500) if Redis is down."""
    db = AsyncMock()
    token = "fake_token"
    public_key = "fake_key"

    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis_client = MagicMock()
        mock_redis_client.get = AsyncMock(side_effect=Exception("Redis connection error"))
        mock_redis_client.aclose = AsyncMock()
        mock_redis.return_value = mock_redis_client

        # Valid token decode (for JTI check)
        with patch("jwt.decode", return_value={"jti": "fake_jti"}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db, token, public_key)

            assert exc_info.value.status_code == 500
            assert "Internal server error" in exc_info.value.detail

@pytest.mark.asyncio
async def test_redis_token_revoked():
    """Test that a revoked token raises 401."""
    db = AsyncMock()
    token = "fake_token"
    public_key = "fake_key"

    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis_client = MagicMock()
        mock_redis_client.get = AsyncMock(return_value=b"1") # Revoked
        mock_redis_client.aclose = AsyncMock()
        mock_redis.return_value = mock_redis_client

        with patch("jwt.decode", return_value={"jti": "fake_jti"}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db, token, public_key)

            assert exc_info.value.status_code == 401
            assert "Token has been revoked" in exc_info.value.detail

@pytest.mark.asyncio
async def test_invalid_token_format_caught():
    """Test that invalid token signature raises 403."""
    db = AsyncMock()
    token = "fake_token"
    public_key = "fake_key"

    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis_client = MagicMock()
        mock_redis_client.get = AsyncMock(return_value=None)
        mock_redis_client.aclose = AsyncMock()
        mock_redis.return_value = mock_redis_client

        with patch("jwt.decode", side_effect=jwt.PyJWTError("Invalid signature")):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db, token, public_key)

            assert exc_info.value.status_code == 403
            assert "Could not validate credentials" in exc_info.value.detail

@pytest.mark.asyncio
async def test_clerk_token_validation():
    """Test that Clerk tokens are verified correctly."""
    db = AsyncMock()
    token = "fake_token"
    public_key = "fake_key"

    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis_client = MagicMock()
        mock_redis_client.get = AsyncMock(return_value=None)
        mock_redis_client.aclose = AsyncMock()
        mock_redis.return_value = mock_redis_client

        with patch("jwt.decode") as mock_decode:
            mock_decode.side_effect = [
                {"jti": "jti"}, # 1st: JTI check
                {"iss": settings.CLERK_ISSUER}, # 2nd: Issuer check
                {"sub": "clerk_123"} # 3rd: Actual validation
            ]

            mock_result = MagicMock()
            mock_user = MagicMock()
            mock_user.is_active = True
            mock_result.scalar_one_or_none.return_value = mock_user
            db.execute.return_value = mock_result

            user = await get_current_user(db, token, public_key)
            assert user == mock_user
