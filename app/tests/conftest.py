import pytest
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app
from db.base import Base
from db.session import get_session as original_get_session


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://app:secret@localhost:5432/order"
)


@pytest.fixture(scope="session")
async def engine():
    """Create database engine for tests."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# Database session fixture
@pytest.fixture
async def db_session(engine):
    """Create test database session."""
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

    async def override_get_session():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    # Override dependency
    app.dependency_overrides[original_get_session] = override_get_session

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # Clear overrides
    app.dependency_overrides.clear()


# Async HTTP client fixture
@pytest.fixture
async def async_client():
    """Create async HTTP client for tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0
    ) as client:
        yield client


# Sync client for simple tests
@pytest.fixture
def sync_client():
    """Create sync HTTP client for tests."""
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client
