import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status

from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_invalid_token_does_not_swallow_401():
    db = AsyncMock()
    token = "fake.token.here"
    public_key = "fake_pub_key"

    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = b"1"  # Revoked token

    with patch("app.api.deps.jwt.get_unverified_claims") as mock_jwt_unverified, \
         patch("redis.asyncio.from_url", return_value=mock_redis_client):

        mock_jwt_unverified.return_value = {"jti": "revoked_jti_123"}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=db, token=token, public_key=public_key)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Token has been revoked"
