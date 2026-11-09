import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock
from app.api.deps import get_user_id

def test_get_user_id_malformed_auth_header():
    request = MagicMock()
    request.headers.get.return_value = "BearerMalforedNoSpace"
    request.client.host = "1.2.3.4"

    # It should split by space, which will fail and throw an IndexError
    # get_user_id has a catch-all which returns the ip.

    with patch("app.api.deps.get_remote_address") as mock_get_remote:
        mock_get_remote.return_value = "1.2.3.4"
        res = get_user_id(request)
        assert res == "ip:1.2.3.4"
