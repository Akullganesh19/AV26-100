import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user import UserRole
from sqlalchemy import select
from app.models.user import User

@pytest.mark.asyncio
async def test_register_privilege_escalation(db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/register",
            json={
                "email": "hacker@example.com",
                "name": "Hacker",
                "password": "password123",
                "role": "admin",
                "alert_threshold": 70,
                "email_alerts": True
            },
        )
    assert response.status_code == 201

    # Check database to see if role is still OFFICER (default) instead of admin
    result = await db_session.execute(select(User).where(User.email == "hacker@example.com"))
    user = result.scalar_one()
    assert user.role == UserRole.OFFICER
