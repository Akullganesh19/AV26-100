import pytest
from app.models.user import UserRole
from app.api.routes.auth import register
from app.schemas.user import UserCreate
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
import builtins

@pytest.mark.asyncio
async def test_register_mass_assignment():
    db = AsyncMock()
    # Mock user query to return None (no existing user)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    user_in = UserCreate(email="hacker@example.com", name="hacker", password="123", role=UserRole.ADMIN)

    # We will intercept db.add, using a simple Mock since db.add is synchronous
    db.add = MagicMock(side_effect=lambda user: setattr(db, "added_user", user))

    # Provide a proper request to bypass slowapi issues
    request = Request({"type": "http", "method": "POST", "path": "/register", "headers": [(b"host", b"localhost")]})

    with patch('app.core.security.get_password_hash', return_value="hashed"):
        res = await register(request=request, user_in=user_in, db=db)

        user_added = getattr(db, "added_user", None)
        assert user_added is not None
        assert user_added.role == UserRole.OFFICER
