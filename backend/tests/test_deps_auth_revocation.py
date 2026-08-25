import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_raises_401():
    from app.api.deps import get_current_user

    with patch("redis.asyncio.from_url") as mock_redis_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = b'1'
        mock_redis_from_url.return_value = mock_redis_client

        with patch("app.api.deps.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {"jti": "mock_jti_123", "sub": "mock_user"}
            db_mock = AsyncMock()

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=db_mock, token="mock_token", public_key="mock_pub")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token has been revoked"

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    from app.api.deps import get_current_user
    import app.models # To load all models including user_districts
    from app.models.user import User

    with patch("redis.asyncio.from_url") as mock_redis_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = None
        mock_redis_from_url.return_value = mock_redis_client

        with patch("app.api.deps.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {"jti": "mock_jti_123", "sub": "clerk_mock_user"}

            db_mock = AsyncMock()
            mock_result = MagicMock()

            # Since SQLAlchemy throws a fit if we don't load everything, let's just use a MagicMock for User
            mock_user = MagicMock(spec=User)
            mock_user.is_active = True
            mock_user.clerk_id = "clerk_mock_user"

            mock_result.scalar_one_or_none.return_value = mock_user
            db_mock.execute.return_value = mock_result

            user = await get_current_user(db=db_mock, token="mock_token", public_key="mock_pub")
            assert user.clerk_id == "clerk_mock_user"
