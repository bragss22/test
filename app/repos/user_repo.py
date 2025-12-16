import logging

from core.security import hash_password
from models.user import User
from schemas.user import UserCreate
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: AsyncSession):
        """Инициализация репозитория с асинхронной сессией БД."""
        self.db = db

    async def register(self, user_create: UserCreate) -> User:
        # Хешируем пароль
        logger.info(f"[HASH] Получен пароль: '{user_create.password}'")
        logger.info(f'[HASH] Длина в символах: {len(user_create.password)}')
        logger.info(f"[HASH] Длина в байтах: {len(user_create.password.encode('utf-8'))}")
        hashed_password = hash_password(user_create.password)

        # Создаем объект User для вставки
        user_data = {
            'email': user_create.email,
            'hashed_password': hashed_password
        }

        # Выполняем вставку
        stmt = insert(User).values(**user_data).returning(User)
        result = await self.db.execute(stmt)
        user = result.scalar_one()

        # Коммитим изменения
        await self.db.commit()

        # Обновляем объект из БД
        await self.db.refresh(user)

        return user

    async def get_user(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        res = await self.db.execute(stmt)
        return res.scalars().first()
