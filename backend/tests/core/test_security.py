from datetime import timedelta
from jose import jwt
import pytest

from app.core.security import create_access_token, decode_token
from app.core.config import settings

def test_decode_token():
    subject = "testuser"
    token = create_access_token(subject=subject, expires_delta=timedelta(minutes=15))

    decoded = decode_token(token)

    assert "sub" in decoded
    assert decoded["sub"] == subject
    assert "exp" in decoded

def test_decode_token_invalid():
    with pytest.raises(jwt.JWTError):
        decode_token("invalid_token")
