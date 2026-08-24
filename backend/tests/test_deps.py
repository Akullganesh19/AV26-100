import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_revoked_token_raises_401():
    db_mock = AsyncMock()
    token = "dummy_token"
    public_key = "dummy_key"

    with patch("jose.jwt.get_unverified_claims", return_value={"jti": "123"}), \
         patch("redis.asyncio.from_url") as redis_mock:

        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.return_value = b"revoked"
        redis_mock.return_value = mock_redis_instance

        with patch("jose.jwt.decode"): # mock decode so it doesn't fail if we reach it
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=db_mock, token=token, public_key=public_key)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token has been revoked"

@pytest.mark.asyncio
async def test_redis_unreachable_falls_through():
    db_mock = AsyncMock()
    # Use MagicMock for user and result so that scalar_one_or_none doesn't return a coroutine
    mock_user = MagicMock()
    mock_user.is_active = True
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    db_mock.execute.return_value = mock_result

    token = "dummy_token"
    public_key = "dummy_key"

    with patch("jose.jwt.get_unverified_claims", return_value={"jti": "123"}), \
         patch("redis.asyncio.from_url") as redis_mock:

        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.side_effect = Exception("Connection refused")
        redis_mock.return_value = mock_redis_instance

        with patch("jose.jwt.decode", return_value={"sub": "clerk_123"}):
            # This should succeed and return the mock user instead of raising HTTPException
            user = await get_current_user(db=db_mock, token=token, public_key=public_key)
            assert user == mock_user
