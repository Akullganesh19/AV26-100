import pytest
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    db_mock = AsyncMock()
    token = "fake.jwt.token"
    public_key = "fake_pub_key"

    with patch("app.api.deps.jwt.get_unverified_claims") as mock_claims, \
         patch("redis.asyncio.from_url") as mock_redis:

        mock_claims.return_value = {"jti": "revoked_jti"}
        mock_redis_conn = AsyncMock()
        mock_redis_conn.get.return_value = b"some_value" # Simulate token found in redis
        mock_redis.return_value = mock_redis_conn

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=db_mock, token=token, public_key=public_key)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has been revoked"
