import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.api.deps import get_current_user
from jose import jwt

@pytest.mark.asyncio
async def test_revoked_token_is_rejected():
    # Mock JWT and Redis to simulate a revoked token
    token = "fake.token.here"

    # We need to mock redis.from_url
    with patch("redis.asyncio.from_url") as mock_redis_from_url, \
         patch("jose.jwt.get_unverified_claims") as mock_get_unverified_claims, \
         patch("app.api.deps.settings.CELERY_BROKER_URL", "redis://localhost:6379/0"):

        # Mock Redis client and its get method
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"1"  # Redis returns something if token is revoked
        mock_redis_from_url.return_value = mock_redis

        # Mock get_unverified_claims to return a JTI
        mock_get_unverified_claims.return_value = {"jti": "revoked-jti-123"}

        # We expect get_current_user to raise an HTTPException with 401
        try:
            await get_current_user(db=AsyncMock(), token=token, public_key="fake_key")
            pytest.fail("HTTPException was not raised. Revoked token was accepted!")
        except HTTPException as e:
            assert e.status_code == 401
            assert e.detail == "Token has been revoked"
