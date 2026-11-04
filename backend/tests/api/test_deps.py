import pytest
from fastapi import HTTPException, status
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_raises_401(mocker):
    # Mock redis and jwt
    mock_redis = mocker.patch("redis.asyncio.from_url")
    mock_redis_instance = mocker.AsyncMock()
    mock_redis_instance.get.return_value = b"1" # Token is revoked
    mock_redis.return_value = mock_redis_instance

    mock_jwt = mocker.patch("app.api.deps.jwt.get_unverified_claims")
    mock_jwt.return_value = {"jti": "revoked-id"}

    mock_db = mocker.MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db=mock_db, token="mocked-token", public_key="mocked-key")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Token has been revoked"
