import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings

# In the backend test configuration (`conftest.py`), when constructing the `TEST_DATABASE_URL` dynamically from `settings.DATABASE_URL`, ensure the logic checks if the base URL already ends with `_test` before appending it (e.g., `db_url_str if db_url_str.endswith("_test") else f"{db_url_str}_test"`). This avoids appending `_test` multiple times resulting in `InvalidCatalogNameError` for non-existent databases like `episense_test_test`.
db_url_str = str(settings.DATABASE_URL)
TEST_DATABASE_URL = db_url_str if db_url_str.endswith("_test") else f"{db_url_str}_test"

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
