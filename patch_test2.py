import asyncio
from sqlalchemy import select
from app.models.user import User
from app.models.district import District
from app.models.user_district import user_district_association
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"
engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check():
    async with TestSessionLocal() as session:
        result = await session.execute(select(District).limit(1))
        d = result.scalar_one_or_none()
        print("District:", d.id)

        query = (
            select(User)
            .join(user_district_association, User.id == user_district_association.c.user_id)
            .where(
                user_district_association.c.district_id == d.id,
                User.email_alerts.is_(True),
                User.alert_threshold <= 88.0,
                User.is_active.is_(True)
            )
        )
        result = await session.execute(query)
        users = result.scalars().all()
        print("Filtered users:", users)

asyncio.run(check())
