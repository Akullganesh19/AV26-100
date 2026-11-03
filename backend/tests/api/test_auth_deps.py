import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_raises_exception():
    db = AsyncMock()
    token = "fake.jwt.token"

    with patch("app.api.deps.jwt.get_unverified_claims") as mock_get_claims, \
         patch("redis.asyncio.from_url") as mock_redis_from_url:

        mock_get_claims.return_value = {"jti": "123"}
        mock_r = AsyncMock()
        mock_r.get.return_value = b'1'  # Revoked
        mock_redis_from_url.return_value = mock_r

        with patch("app.api.deps.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "user_id"}
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = type('User', (), {"is_active": True})()
            db.execute.return_value = mock_result

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=db, token=token, public_key="fake")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token has been revoked"

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    db = AsyncMock()
    token = "fake.jwt.token"

    with patch("app.api.deps.jwt.get_unverified_claims") as mock_get_claims, \
         patch("redis.asyncio.from_url") as mock_redis_from_url:

        mock_get_claims.return_value = {"jti": "123"}
        mock_r = AsyncMock()
        mock_r.get.return_value = None  # Not revoked
        mock_redis_from_url.return_value = mock_r

        with patch("app.api.deps.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "user_id"}
            mock_result = MagicMock()
            user = type('User', (), {"is_active": True})()
            mock_result.scalar_one_or_none.return_value = user
            db.execute.return_value = mock_result

            result = await get_current_user(db=db, token=token, public_key="fake")
            assert result == user
