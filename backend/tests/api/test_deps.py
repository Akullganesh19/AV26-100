import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

# Need to set these before importing get_current_user to avoid initialization errors
import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["SECRET_KEY"] = "asdf"
os.environ["CLERK_PEM_PUBLIC_KEY"] = "dummy"
os.environ["CLERK_ISSUER"] = "dummy"
os.environ["CLERK_AUDIENCE"] = "dummy"

from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    """
    Test that a revoked token correctly raises a 401 HTTP Exception
    and does NOT fall through to the broad exception handler.
    """
    # 1. Mock Redis to simulate a revoked token
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b'1' # token is found in revocation list

    # 2. Mock JWT get_unverified_claims to return a valid JTI
    with patch('redis.asyncio.from_url', return_value=mock_redis):
        with patch('jose.jwt.get_unverified_claims', return_value={'jti': '123'}):
            mock_db = AsyncMock()

            # This should raise a 401 Unauthorized
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(db=mock_db, token='revoked.token.string', public_key='key')

            assert excinfo.value.status_code == 401
            assert excinfo.value.detail == "Token has been revoked"
