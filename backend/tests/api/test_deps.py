import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token_raises_401():
    # Mock redis and its get method to return True (simulating revoked token)
    mock_redis = AsyncMock()
    mock_redis.get.return_value = True

    # We need to mock redis.asyncio.from_url since it's imported locally in the function
    with patch("app.api.deps.jwt.get_unverified_claims", return_value={"jti": "dummy-jti"}):
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            try:
                await get_current_user(db=AsyncMock(), token="dummy-token", public_key="dummy-key")
                assert False, "Expected HTTPException"
            except HTTPException as e:
                assert e.status_code == 401
                assert e.detail == "Token has been revoked"
