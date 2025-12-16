from db.session import get_session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from repos.user_repo import UserRepository
from schemas.user import Token, UserCreate
from services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post('/register/', status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    """Зарегистрировать нового пользователя."""
    repo = UserRepository(db)
    svc = UserService(repo)
    user_db = await svc.register(user=payload)
    return {'id': user_db.id, 'email': user_db.email}


@router.post('/token/', response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """Аутентификация пользователя по паролю. При успехе вернуть JWT access token."""
    repo = UserRepository(db)
    svc = UserService(repo)
    try:
        user_token = await svc.get_token(email=form_data.username, password=form_data.password)
    except Exception as e:
        raise e
    return user_token
