import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, HTTPException
from jose import jwt
from app.api.deps import get_user_id, get_current_user
from app.core.config import settings

def test_get_user_id_spoofing():
    request = Mock(spec=Request)
    request.client = Mock(host="1.2.3.4")

    from slowapi.util import get_remote_address
    def mock_get_remote_address(req):
        return "1.2.3.4"

    spoofed_token = jwt.encode({"sub": "spoofed_user_id"}, "wrong_secret", algorithm="HS256")

    request.headers = {"Authorization": f"Bearer {spoofed_token}"}

    with patch("app.api.deps.get_remote_address", mock_get_remote_address):
        user_id = get_user_id(request)

        assert user_id == "ip:1.2.3.4", f"Expected IP fallback, but got {user_id}"

def test_get_user_id_valid_token():
    request = Mock(spec=Request)
    request.client = Mock(host="1.2.3.4")

    from slowapi.util import get_remote_address
    def mock_get_remote_address(req):
        return "1.2.3.4"

    valid_token = jwt.encode({"sub": "valid_user"}, settings.SECRET_KEY, algorithm="HS256")

    request.headers = {"Authorization": f"Bearer {valid_token}"}

    with patch("app.api.deps.get_remote_address", mock_get_remote_address):
        user_id = get_user_id(request)

        assert user_id == "user:valid_user", f"Expected user_id, but got {user_id}"

@pytest.mark.asyncio
async def test_get_current_user_revocation_bypass():
    db = AsyncMock()

    token = jwt.encode({"jti": "revoked_id", "sub": "user_1"}, settings.SECRET_KEY, algorithm="HS256")
    public_key = settings.CLERK_PEM_PUBLIC_KEY

    class FakeRedis:
        async def get(self, key):
            return True
        async def aclose(self):
            pass

    def fake_from_url(*args, **kwargs):
        return FakeRedis()

    with patch("redis.asyncio.from_url", side_effect=fake_from_url):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(db=db, token=token, public_key=public_key)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token has been revoked"
