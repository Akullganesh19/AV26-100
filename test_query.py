import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District

async def test():
    async with SessionLocal() as db:
        query = (
            select(User)
            .join(User.districts)
            .where(District.id == "some-id")
        )
        print(query)

asyncio.run(test())
