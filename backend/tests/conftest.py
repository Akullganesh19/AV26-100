import pytest
import pytest_asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings

# In CI we set DATABASE_URL to exactly what we want to connect to.
# However, the previous logic unconditionally appended "_test".
# If the environment variable DATABASE_URL already has the test DB name,
# we should not append it.
db_url_str = str(settings.DATABASE_URL).rstrip("/")
if not db_url_str.endswith("_test"):
    TEST_DATABASE_URL = db_url_str + "_test"
else:
    TEST_DATABASE_URL = db_url_str

@pytest_asyncio.fixture
async def db_session():
    """
    Creates a fresh database session for each test, 
    ensuring loop consistency and data isolation.
    """
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        # Reset schema for each test run
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
    
    await engine.dispose()
