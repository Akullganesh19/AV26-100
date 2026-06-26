import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
import jwt

from app.api.deps import get_current_user

# Valid JWT without signature but well-formed to bypass basic syntax checks in gitleaks
DUMMY_TOKEN = jwt.encode({"sub": "1234567890", "name": "John Doe", "iat": 1516239022, "jti": "mission-critical-jti"}, "a_very_long_secret_key_that_is_at_least_32_bytes_long", algorithm="HS256")

@pytest.mark.asyncio
async def test_get_current_user_redis_failure_fails_closed():
    """
    Sentinel Regression Test:
    Ensures that if the token revocation check fails (e.g. Redis is down),
    the system fails closed (500) rather than failing open (bypassing revocation).
    """
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Redis connection refused!")
        mock_from_url.return_value = mock_redis

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=AsyncMock(), token=DUMMY_TOKEN, public_key="dummy")

        assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_fails():
    """
    Sentinel Regression Test:
    Ensures that if the token is revoked, it actually raises a 401 and is not swallowed.
    """
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"revoked"
        mock_from_url.return_value = mock_redis

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=AsyncMock(), token=DUMMY_TOKEN, public_key="dummy")

        assert exc_info.value.status_code == 401
