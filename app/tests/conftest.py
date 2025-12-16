import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from db.base import Base
from db.session import get_session as original_get_session
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.pool import NullPool

# Используем тестовую базу данных
TEST_DATABASE_URL = os.getenv(
    'TEST_DATABASE_URL',
    'postgresql+asyncpg://test_user:test_password@localhost:5433/test_db'
)


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Отключаем для чистоты вывода
        poolclass=NullPool,  # Не используем пул для тестов
        future=True,
    )

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очищаем после всех тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
async def override_get_session(db_session: AsyncSession):
    """Override the get_session dependency."""

    async def _override_get_session():
        try:
            yield db_session
        finally:
            # Не закрываем сессию здесь, она будет закрыта в db_session фикстуре
            pass

    app.dependency_overrides[original_get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_session) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP test client."""
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://testserver',
            timeout=30.0,
    ) as client:
        yield client


@pytest.fixture(autouse=True)
async def cleanup_test_data(db_session):
    """Автоматическая очистка тестовых данных после каждого теста."""
    yield

    try:
        # Используем text() для текстовых SQL запросов
        await db_session.execute(text('SET CONSTRAINTS ALL DEFERRED'))
        tables = ['orders', 'users']  # Порядок важен для foreign key constraints

        for table in tables:
            try:
                await db_session.execute(text(f'TRUNCATE TABLE {table} CASCADE'))
            except Exception as e:
                print(f'Warning: Could not truncate table {table}: {e}')

        await db_session.commit()
    except Exception:
        await db_session.rollback()
        raise
    finally:
        await db_session.close()
        pass
