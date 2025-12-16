from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.base import Base
from core.config import settings

# Создание асинхронного движка базы данных
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
# Настройка локальной асинхронной сессии
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def async_init_db():
	"""Создать таблицы в БД при старте (упрощённо, вместо миграций)."""
	# Для простоты: создаем таблицы, если они не существуют. В продакшене используйте миграции Alembic.
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
	"""Депенденси FastAPI: предоставить асинхронную сессию для обработки запроса."""
	async with AsyncSessionLocal() as session:
		yield session
