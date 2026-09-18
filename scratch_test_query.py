import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User

async def run():
    async with SessionLocal() as db:
        query = select(User).where(User.email_alerts == True)
        result = await db.execute(query)
        users = result.scalars().all()
        print(users)

if __name__ == "__main__":
    asyncio.run(run())
