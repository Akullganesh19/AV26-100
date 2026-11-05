import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_get_current_user_revoked_token(mocker):
    # Mock JWT claims
    mock_jwt = mocker.patch("app.api.deps.jwt.get_unverified_claims")
    mock_jwt.return_value = {"jti": "mock_jti"}

    # Mock Redis
    mock_redis_instance = AsyncMock()
    mock_redis_instance.get.return_value = b"true"
    mock_redis_instance.aclose = AsyncMock()

    mock_from_url = mocker.patch("redis.asyncio.from_url")
    mock_from_url.return_value = mock_redis_instance

    # Mock DB, token, public key
    mock_db = MagicMock()
    token = "mock_token"
    public_key = "mock_key"

    # Test that HTTPException is raised and not swallowed
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db=mock_db, token=token, public_key=public_key)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"
