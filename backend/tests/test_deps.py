import pytest
from unittest.mock import MagicMock, patch
from fastapi import Request, HTTPException
from jose import jwt
from app.api.deps import get_user_id, get_current_user
from app.core.config import settings

def test_get_user_id_unverified_token():
    token = jwt.encode({"sub": "attacker"}, "random_secret", algorithm="HS256")
    req = MagicMock(spec=Request)
    req.headers = {"Authorization": f"Bearer {token}"}
    req.client = MagicMock()
    req.client.host = "127.0.0.1"

    user_id = get_user_id(req)
    assert user_id == "ip:127.0.0.1", f"Expected IP, got {user_id}"

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    token = jwt.encode({"sub": "victim", "jti": "revoked-123"}, "secret", algorithm="HS256")

    class FakeRedis:
        async def get(self, key):
            if key == "revoked_token:revoked-123":
                return b"1"
            return None
        async def aclose(self):
            pass

    with patch("redis.asyncio.from_url", return_value=FakeRedis()):
        db = MagicMock()
        try:
            await get_current_user(db=db, token=token, public_key="key")
            pytest.fail("Should have raised HTTPException 401")
        except HTTPException as e:
            assert e.status_code == 401
            assert e.detail == "Token has been revoked"
