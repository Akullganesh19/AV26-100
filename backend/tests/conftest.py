import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import app.models  # Ensure all models are loaded before Base.metadata.create_all
from app.core.database import Base
from app.core.config import settings
import os

# Use the dedicated test database created in the previous step,
# unless we are running in CI (GitHub Actions) where the DB is already episodic_test
if os.environ.get("GITHUB_ACTIONS") == "true":
    TEST_DATABASE_URL = str(settings.DATABASE_URL)
else:
    TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

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
