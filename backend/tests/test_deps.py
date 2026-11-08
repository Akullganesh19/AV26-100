import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.api.deps import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_get_current_user_revoked_token(mocker):
    # Mock JWT payload
    mocker.patch(
        "app.api.deps.jwt.get_unverified_claims",
        return_value={"jti": "revoked-id", "sub": "user_1"}
    )

    # Mock Redis
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=b"1") # Simulate token is revoked
    mock_redis.aclose = AsyncMock()
    mocker.patch("redis.asyncio.from_url", return_value=mock_redis)

    db_mock = AsyncMock(spec=AsyncSession)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(db=db_mock, token="dummy_token", public_key="dummy_key")

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token has been revoked"
