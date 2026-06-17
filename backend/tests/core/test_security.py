import pytest
from datetime import timedelta
from jose import jwt

from app.core.security import create_access_token
from app.core.config import settings

def test_create_access_token():
    subject = "test_user_id"
    token = create_access_token(subject=subject)

    assert isinstance(token, str)

    # Verify the token can be decoded
    decoded_token = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded_token["sub"] == subject
    assert "exp" in decoded_token

def test_create_access_token_with_expires_delta():
    subject = "test_user_id"
    expires_delta = timedelta(minutes=15)
    token = create_access_token(subject=subject, expires_delta=expires_delta)

    assert isinstance(token, str)

    # Verify the token can be decoded
    decoded_token = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded_token["sub"] == subject
    assert "exp" in decoded_token
