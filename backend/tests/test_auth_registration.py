import pytest
from httpx import AsyncClient
import uuid
from app.main import app
from app.models.user import UserRole
from app.api.deps import get_db

@pytest.mark.asyncio
async def test_register_privilege_escalation(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": f"hacker_{uuid.uuid4().hex[:8]}@example.com",
                "name": "Hacker",
                "password": "password123",
                "role": "sysadmin"
            }
        )

    assert response.status_code == 201
    user_data = response.json()

    # Assert that the created user does NOT have the requested sysadmin role
    # but rather the default role.
    assert user_data["role"] == UserRole.OFFICER.value
