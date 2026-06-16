from app.core.security import get_password_hash, verify_password

def test_get_password_hash():
    password = "supersecretpassword123"
    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0

def test_verify_password_success():
    password = "supersecretpassword123"
    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password) is True

def test_verify_password_failure():
    password = "supersecretpassword123"
    wrong_password = "wrongpassword"
    hashed_password = get_password_hash(password)

    assert verify_password(wrong_password, hashed_password) is False
