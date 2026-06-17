import pytest
from app.core.security import get_password_hash, verify_password

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert password != hashed
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

def test_verify_invalid_hash_format():
    assert not verify_password("secret_password", "invalid_hash_string")
