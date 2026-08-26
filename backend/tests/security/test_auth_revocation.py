import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock, AsyncMock
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_raises_401():
    """
    Sentinel regression test: Proves that a revoked token correctly raises
    a 401 Unauthorized exception, and that the exception is NOT swallowed
    by the broad Exception handler in get_current_user.
    """
    # Mock JWT claims with a JTI
    mock_payload = {"jti": "mock-jti", "sub": "mock-user"}

    with patch("app.api.deps.jwt.get_unverified_claims", return_value=mock_payload):
        # Mock Redis to simulate token found in revocation list
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=b'1') # Simulates token is revoked
        mock_redis.aclose = AsyncMock()

        with patch("redis.asyncio.from_url", return_value=mock_redis):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=MagicMock(), token="mock-token", public_key="mock-key")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token has been revoked"
