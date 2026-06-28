import asyncio
from sqlalchemy import select
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"
engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check():
    async with TestSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print("Users:", users)
        result = await session.execute(select(District))
        districts = result.scalars().all()
        print("Districts:", districts)

        # user districts
        result = await session.execute(select(user_district_association))
        ud = result.all()
        print("User districts:", ud)

asyncio.run(check())
