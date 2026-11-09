import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_raises_401():
    token = "fake.token.here"
    public_key = "fake_key"
    db_mock = AsyncMock()

    with patch("redis.asyncio.from_url") as mock_redis, \
         patch("app.api.deps.jwt.get_unverified_claims") as mock_get_claims:

        mock_r = AsyncMock()
        mock_r.get.return_value = b'1'
        mock_redis.return_value = mock_r

        mock_get_claims.return_value = {"jti": "12345"}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=db_mock, token=token, public_key=public_key)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has been revoked"
