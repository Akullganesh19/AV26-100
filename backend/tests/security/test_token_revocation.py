import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    mock_db = AsyncMock()

    with patch("jose.jwt.get_unverified_claims", return_value={"jti": "revoked_id"}):
        with patch("redis.asyncio.from_url") as mock_redis_from_url:
            mock_redis = AsyncMock()
            mock_redis.get.return_value = True # Token is revoked
            mock_redis_from_url.return_value = mock_redis

            with patch("jose.jwt.decode") as mock_decode:
                mock_decode.side_effect = Exception("invalid token")
                with pytest.raises(HTTPException) as excinfo:
                    await get_current_user(db=mock_db, token="dummy_token", public_key="dummy_key")

                assert excinfo.value.status_code == 401
                assert "revoked" in excinfo.value.detail
