import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings

# Use the dedicated test database created in the previous step
TEST_DATABASE_URL = str(settings.DATABASE_URL).rstrip("/")
if not TEST_DATABASE_URL.endswith("_test"):
    TEST_DATABASE_URL += "_test"

@pytest_asyncio.fixture
async def db_session():
    """
    Creates a fresh database session for each test, 
    ensuring loop consistency and data isolation.
    """
    engine = create_async_engine(TEST_DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            # Reset schema for each test run
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        pytest.skip(f"Skipping DB tests due to connection error: {e}")
        return

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
    
    await engine.dispose()
