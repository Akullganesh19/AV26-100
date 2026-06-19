import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings

# Explicitly import all models so that Base.metadata.create_all works correctly
import app.models

# In CI and test environments, we need to ensure the test DB URL doesn't get mangled.
# conftest.py used to append "_test" to the URL.
# However, if the environment variable DATABASE_URL is already pointing to `episense_test`,
# appending "_test" results in `episense_test_test`, which doesn't exist and causes InvalidCatalogNameError.
TEST_DATABASE_URL = str(settings.DATABASE_URL)
if not TEST_DATABASE_URL.endswith("_test"):
    TEST_DATABASE_URL += "_test"

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
