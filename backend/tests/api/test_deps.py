import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_raises_401():
    # Mock db and token
    mock_db = AsyncMock()
    token = "fake_revoked_token"
    public_key = "fake_public_key"

    # We need to patch redis.from_url to return a mock redis client
    mock_redis_client = AsyncMock()
    # r.get returns something truthy when the token is revoked
    mock_redis_client.get.return_value = b'1'

    # We need to mock jwt.get_unverified_claims
    mock_jwt = {
        "jti": "mock-jti"
    }

    with patch("redis.asyncio.from_url", return_value=mock_redis_client):
        with patch("app.api.deps.jwt.get_unverified_claims", return_value=mock_jwt):
            # The function should raise a 401 HTTPException because the token is revoked.
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=mock_db, token=token, public_key=public_key)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token has been revoked"
