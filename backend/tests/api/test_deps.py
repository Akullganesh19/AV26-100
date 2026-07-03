import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_bypassed():
    # We want to test that if a token is revoked, it should raise HTTPException, NOT fall through

    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b'1' # simulate revoked token found

    # We patch redis.from_url to return our mock_redis
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        # We patch jwt.get_unverified_claims to return a JTI
        with patch("jose.jwt.get_unverified_claims", return_value={"jti": "test_jti"}):
            try:
                await get_current_user(db=mock_db, token="fake_token", public_key="fake_key")
                assert False, "Should have raised HTTPException"
            except HTTPException as e:
                assert e.status_code == 401
                assert e.detail == "Token has been revoked"


from redis.exceptions import RedisError

@pytest.mark.asyncio
async def test_get_current_user_redis_failure_fails_closed():
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = RedisError("Connection refused")

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        with patch("jose.jwt.get_unverified_claims", return_value={"jti": "test_jti"}):
            try:
                await get_current_user(db=mock_db, token="fake_token", public_key="fake_key")
                assert False, "Should have raised HTTPException for Redis failure"
            except HTTPException as e:
                assert e.status_code == 500
                assert e.detail == "Authentication infrastructure unavailable"
