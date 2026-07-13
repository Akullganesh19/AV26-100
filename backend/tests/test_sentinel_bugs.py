import pytest
import asyncio
from fastapi import HTTPException
from app.api.deps import get_current_user
from app.api.routes.auth import register
from app.schemas.user import UserCreate
from app.models.user import UserRole, User

@pytest.mark.asyncio
async def test_register_mass_assignment():
    # Attempt to register as an ADMIN
    user_data = UserCreate(
        email="hacker@evil.com",
        name="Hacker",
        password="password123",
        role=UserRole.ADMIN
    )

    # Mock db and request
    class MockDB:
        async def execute(self, *args, **kwargs):
            class MockResult:
                def scalar_one_or_none(self):
                    return None
            return MockResult()
        def add(self, user):
            self.added_user = user
        async def commit(self):
            pass
        async def refresh(self, user):
            user.id = "mock_id"

    db = MockDB()
    # Call register
    try:
        new_user = await register(request=None, user_in=user_data, db=db)
        assert new_user.role != UserRole.ADMIN, "VULNERABLE: Mass assignment allowed setting ADMIN role"
    except Exception as e:
        if isinstance(e, AssertionError):
            raise
        # Other errors are fine for this basic test

@pytest.mark.asyncio
async def test_token_revocation_bypass():
    import redis.asyncio as redis
    from jose import jwt
    from app.core.config import settings

    # Mock token
    token = jwt.encode({"sub": "test_user", "jti": "revoked_jti"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Mock Redis to simulate revoked token
    class MockRedis:
        async def get(self, key):
            if key == "revoked_token:revoked_jti":
                return b"1"
            return None
        async def aclose(self):
            pass

    old_from_url = redis.from_url
    redis.from_url = lambda url: MockRedis()

    class MockDB:
        pass

    try:
        # Call get_current_user with revoked token
        # Should raise HTTPException 401
        try:
            await get_current_user(db=MockDB(), token=token, public_key="mock_key")
            assert False, "VULNERABLE: Revoked token was accepted!"
        except HTTPException as e:
            assert e.status_code == 401, f"Expected 401, got {e.status_code}"
            assert "revoked" in e.detail.lower()
    finally:
        redis.from_url = old_from_url

@pytest.mark.asyncio
async def test_token_revocation_fail_open():
    import redis.asyncio as redis
    from jose import jwt
    from app.core.config import settings

    token = jwt.encode({"sub": "test_user", "jti": "some_jti"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Mock Redis to raise connection error
    class MockRedisError(redis.RedisError):
        pass

    class MockRedisDown:
        async def get(self, key):
            raise MockRedisError("Connection refused")
        async def aclose(self):
            pass

    old_from_url = redis.from_url
    redis.from_url = lambda url: MockRedisDown()

    class MockDB:
        pass

    try:
        # Call get_current_user with redis down
        try:
            await get_current_user(db=MockDB(), token=token, public_key="mock_key")
            assert False, "VULNERABLE: Failed open when Redis was down!"
        except HTTPException as e:
            assert e.status_code == 500, f"Expected 500 when Redis is down, got {e.status_code}"
    finally:
        redis.from_url = old_from_url
