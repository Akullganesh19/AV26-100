import pytest
import asyncio
from fastapi import HTTPException
from app.api.deps import get_current_user
import redis.asyncio

# We will mock Redis and token decoding to show it bypasses revocation
@pytest.mark.asyncio
async def test_fail_open_revocation(mocker):
    # Mock jwt.get_unverified_claims to return a valid jti
    mocker.patch('app.api.deps.jwt.get_unverified_claims', return_value={"jti": "123", "sub": "user_1"})

    # Mock Redis to simulate a revoked token
    class MockRedis:
        async def get(self, key):
            return b"revoked" # Simulating token is revoked
        async def aclose(self):
            pass

    mocker.patch('redis.asyncio.from_url', return_value=MockRedis())

    # Mock jwt.decode (standard verification) to SUCCEED
    mocker.patch('app.api.deps.jwt.decode', return_value={"sub": "user_1"})

    # Mock DB
    class MockResult:
        def scalar_one_or_none(self):
            class MockUser:
                id = 1
                is_active = True
            return MockUser()

    class MockDB:
        async def execute(self, query):
            return MockResult()

    # Run the dependency
    # If the vulnerability exists, it will NOT raise HTTPException(401), it will return the user
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db=MockDB(), token="valid_token", public_key="key")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"
