import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_revoked_token_raises_401(mocker):
    # Mock settings to avoid trying to connect to real Redis during test
    mocker.patch("app.api.deps.settings.CELERY_BROKER_URL", "redis://localhost:6379/0")

    # Mock redis instance and its get method to return True (simulating revoked)
    mock_redis_instance = mocker.AsyncMock()
    mock_redis_instance.get.return_value = b'1'
    mocker.patch("redis.asyncio.from_url", return_value=mock_redis_instance)

    # Mock jwt.get_unverified_claims to return a valid jti
    mocker.patch("app.api.deps.jwt.get_unverified_claims", return_value={"jti": "mock_jti"})

    mock_db = mocker.AsyncMock()
    mock_token = "mock_token"
    mock_public_key = "mock_key"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db=mock_db, token=mock_token, public_key=mock_public_key)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"
