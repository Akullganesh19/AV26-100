import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException, Request
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_does_not_swallow_http_exception():
    db = AsyncMock()
    token = "fake_token"
    public_key = "fake_key"

    with patch("app.api.deps.jwt.get_unverified_claims") as mock_unverified:
        mock_unverified.return_value = {"jti": "fake_jti"}

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.get.return_value = b"revoked"
            mock_redis.return_value = mock_redis_instance

            with patch("app.api.deps.select") as mock_select:
                mock_result = MagicMock()
                mock_user = MagicMock()
                mock_user.is_active = True
                mock_result.scalar_one_or_none.return_value = mock_user
                db.execute.return_value = mock_result

                try:
                    await get_current_user(db, token, public_key)
                    assert False, "Should have raised 401 Unauthorized"
                except HTTPException as e:
                    assert e.status_code == 401
                except Exception as e:
                    assert False, f"Raised unexpected exception: {e}"
