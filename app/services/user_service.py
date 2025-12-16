from repos.user_repo import UserRepository
from models.user import User
from schemas.user import UserCreate


class UserService:
    def __init__(self, repo: UserRepository):
        """Инициализация сервиса пользователей с заданным репозиторием."""
        self.repo = repo

    async def register(self, user: UserCreate) -> User:
        """Создать пользователя."""
        return await self.repo.register(user_create=user)

