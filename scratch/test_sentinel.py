import asyncio
from app.schemas.user import UserCreate

def test_mass_assignment():
    data = {
        "email": "hacker@evil.com",
        "name": "Hacker",
        "password": "password",
        "role": "admin"
    }
    user = UserCreate(**data)
    print("User role:", user.role)

test_mass_assignment()
