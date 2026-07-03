import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
import redis

# Need to set these before importing get_current_user to avoid initialization errors
import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["SECRET_KEY"] = "asdf"
os.environ["CLERK_PEM_PUBLIC_KEY"] = "dummy"
os.environ["CLERK_ISSUER"] = "dummy"
os.environ["CLERK_AUDIENCE"] = "dummy"

from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_redis_error():
    """
    Test that a RedisError results in a 500 error (fails closed).
    """
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = redis.RedisError("Connection failed")

    with patch('redis.asyncio.from_url', return_value=mock_redis):
        with patch('jose.jwt.get_unverified_claims', return_value={'jti': '123'}):
            mock_db = AsyncMock()

            # This should raise a 500 Internal Server Error
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(db=mock_db, token='valid.token.string', public_key='key')

            assert excinfo.value.status_code == 500
            assert excinfo.value.detail == "Authentication service unavailable"
