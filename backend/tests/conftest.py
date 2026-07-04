import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings

# Use the dedicated test database created in the previous step
TEST_DATABASE_URL = str(settings.DATABASE_URL)
if not TEST_DATABASE_URL.endswith("_test"):
    TEST_DATABASE_URL += "_test"

@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    """
    Creates a fresh database session for each test,
    ensuring loop consistency and data isolation.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
