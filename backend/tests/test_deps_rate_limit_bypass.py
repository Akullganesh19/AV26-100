import pytest
from unittest.mock import MagicMock, patch
from fastapi import Request
from jose import jwt

# We need to import the get_user_id function
from app.api.deps import get_user_id
from app.core.config import settings

def test_get_user_id_unverified_claims_spoof():
    # Setup request with a spoofed JWT where 'sub' is arbitrary
    token = jwt.encode({"sub": "attacker_fake_id_999"}, "fake_key", algorithm="HS256")

    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"Authorization": f"Bearer {token}"}

    # Mock settings to not have PEM or have wrong PEM
    # (Actually we want to test that it fails validation and falls back to IP)

    with patch('app.api.deps.get_remote_address', return_value="1.2.3.4"):
        result = get_user_id(mock_request)
        assert result == "ip:1.2.3.4", f"Expected fallback to IP, got {result}"
