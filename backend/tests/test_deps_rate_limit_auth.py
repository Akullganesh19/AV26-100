from fastapi import Request
from jose import jwt
import pytest
from app.api.deps import get_user_id
from app.core.config import settings

def mock_request(token=None, ip="192.168.1.1"):
    scope = {
        "type": "http",
        "client": (ip, 1234),
        "headers": []
    }
    if token:
        scope["headers"].append((b"authorization", f"Bearer {token}".encode()))
    return Request(scope)

def test_get_user_id_valid_token():
    valid_token = jwt.encode({"sub": "user123"}, settings.SECRET_KEY, algorithm="HS256")
    req = mock_request(valid_token)
    assert get_user_id(req) == "user:user123"

def test_get_user_id_spoofed_token():
    spoofed_token = jwt.encode({"sub": "user_victim"}, "wrong_key", algorithm="HS256")
    req = mock_request(spoofed_token)
    assert get_user_id(req) == "ip:192.168.1.1"

def test_get_user_id_no_token():
    req = mock_request()
    assert get_user_id(req) == "ip:192.168.1.1"
