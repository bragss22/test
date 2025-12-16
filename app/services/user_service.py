from core.security import create_access_token, verify_password
from fastapi import HTTPException, status
from models.user import User
from repos.user_repo import UserRepository
from schemas.user import Token, UserCreate


class UserService:
    def __init__(self, repo: UserRepository):
        """Инициализация сервиса пользователей с заданным репозиторием."""
        self.repo = repo

    async def register(self, user: UserCreate) -> User:
        """Создать пользователя."""
        try:
            user = await self.repo.register(user_create=user)
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Такой пользователь уже есть в БД')
        return user

    async def get_token(self, email: str, password: str) -> Token:
        """Получение токена."""
        user = await self.repo.get_user(email=email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
        access = create_access_token(subject=str(user.id))
        return Token(access_token=access)
