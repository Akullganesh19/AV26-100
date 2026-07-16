import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings
import app.models # make sure tables are registered

# Use the dedicated test database created in the previous step
TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

@pytest_asyncio.fixture
async def db_session():
    """
    Creates a fresh database session for each test, 
    ensuring loop consistency and data isolation.
    """
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        # Avoid foreign key constraint issues when dropping tables
        await conn.execute(pytest.importorskip("sqlalchemy").text("DROP SCHEMA public CASCADE;"))
        await conn.execute(pytest.importorskip("sqlalchemy").text("CREATE SCHEMA public;"))
        await conn.execute(pytest.importorskip("sqlalchemy").text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(pytest.importorskip("sqlalchemy").text("GRANT ALL ON SCHEMA public TO public;"))
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
    
    await engine.dispose()
