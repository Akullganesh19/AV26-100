import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user

@pytest.mark.asyncio
async def test_revoked_token_raises_401(mocker):
    # Mock settings and redis
    mocker.patch("app.api.deps.settings.CELERY_BROKER_URL", "redis://localhost:6379/0")

    class MockRedis:
        async def get(self, key):
            return b"1"
        async def aclose(self):
            pass

    mocker.patch("redis.asyncio.from_url", return_value=MockRedis())

    # Mock jwt.get_unverified_claims
    mocker.patch("app.api.deps.jwt.get_unverified_claims", return_value={"jti": "mock-jti"})

    try:
        await get_current_user(db=None, token="fake-token", public_key="fake-key")
        pytest.fail("Should have raised HTTPException 401")
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Token has been revoked"
