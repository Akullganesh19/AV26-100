import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_get_current_user_revoked_token(mocker):
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b'1'
    mocker.patch('redis.asyncio.from_url', return_value=mock_redis)
    mocker.patch('jose.jwt.get_unverified_claims', return_value={'jti': 'mock-jti'})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(db=AsyncMock(), token='mock-token', public_key='mock-key')
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Token has been revoked'
