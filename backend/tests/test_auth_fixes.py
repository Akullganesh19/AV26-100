import pytest
from app.schemas.user import UserCreate
from app.api.deps import get_user_id
from fastapi import Request
from unittest.mock import MagicMock

def test_user_create_schema():
    data = {
        "email": "attacker@example.com",
        "name": "Attacker",
        "password": "password123",
        "role": "admin"
    }
    # This just ensures we can parse the schema
    user = UserCreate(**data)
    assert user.role.value == "admin" # The schema allows it, but our route overrides it

def test_get_user_id_returns_ip_for_unverified():
    class DummyRequest:
        def __init__(self):
            self.headers = {"Authorization": "Bearer some_token"}
            self.client = MagicMock()
            self.client.host = "1.2.3.4"

        def get(self, key, default=None):
            return self.headers.get(key, default)

    # Normally slowapi gets the IP from request.client.host or headers
    # We'll just pass a MagicMock request and check the prefix
    req = MagicMock(spec=Request)
    req.headers = {"Authorization": "Bearer some_token"}
    req.client = MagicMock()
    req.client.host = "1.2.3.4"
    req.scope = {"type": "http", "client": ("1.2.3.4", 8000)}

    # Testing that it returns the IP instead of extracting the JWT
    from slowapi.util import get_remote_address
    user_id = get_user_id(req)
    assert user_id.startswith("ip:")
