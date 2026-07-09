import pytest
from app.core.security import verify_password, get_password_hash

def test_password_hashing():
    password = "supersecretpassword123!"
    hashed = get_password_hash(password)

    # Should start with $2b$
    assert hashed.startswith("$2b$")

    # Should verify correctly
    assert verify_password(password, hashed) is True

    # Should fail for wrong password
    assert verify_password("wrongpassword", hashed) is False
