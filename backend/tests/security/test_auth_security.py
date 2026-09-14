import pytest
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from app.api.deps import get_current_user, get_user_id
from fastapi import Request

@pytest.mark.asyncio
async def test_revoked_token_is_not_swallowed():
    mock_db = AsyncMock()
    token = "dummy_token"
    mock_pub = "dummy_pub"

    with patch("jose.jwt.get_unverified_claims", return_value={"jti": "revoked_jti"}), \
         patch("redis.asyncio.from_url") as mock_redis_from_url:

        mock_client = AsyncMock()
        mock_client.get.return_value = b"1"
        mock_redis_from_url.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_db, token, mock_pub)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has been revoked"

def test_get_user_id_ignores_unverified_claims():
    mock_request = Request({"type": "http", "headers": [(b"authorization", b"Bearer forged.token.here")]})
    with patch("app.api.deps.get_remote_address", return_value="127.0.0.1"), \
         patch("jose.jwt.get_unverified_claims", return_value={"sub": "attacker"}):

        user_id = get_user_id(mock_request)
        assert user_id == "ip:127.0.0.1"
