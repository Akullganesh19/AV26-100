import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user, get_user_id

class MockRequest:
    def __init__(self, headers):
        self.headers = headers
        self.client = type("Client", (), {"host": "127.0.0.1"})()
        self.scope = {"type": "http"}

def test_get_user_id_invalid_token():
    req = MockRequest({"Authorization": "Bearer invalid_token_here"})
    assert get_user_id(req) == "ip:127.0.0.1"
