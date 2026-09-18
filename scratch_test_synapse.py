import asyncio
from uuid import UUID
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User
from app.models.district import District

async def run():
    async with SessionLocal() as db:
        # Just test the query syntax
        fake_uuid = UUID("12345678-1234-5678-1234-567812345678")
        query = (
            select(User)
            .where(User.districts.any(id=fake_uuid))
            .where(User.email_alerts == True)
            .where(User.alert_threshold <= 90.0)
        )
        print("Query constructed successfully")
        # We won't execute if DB is not up, but we can print the compiled query
        print(query.compile())

if __name__ == "__main__":
    asyncio.run(run())
