from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from db.session import get_session
from models.user import User
from repos.user_repo import UserRepository
from schemas.user import UserCreate, Token
from core.security import verify_password, create_access_token
from services.user_service import UserService

router = APIRouter()


@router.post("/register/", status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    """Зарегистрировать нового пользователя."""
    repo = UserRepository(db)
    svc = UserService(repo)
    user_db = await svc.register(user=payload)
    return {"id": user_db.id, "email": user_db.email}


@router.post("/token/", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """Аутентификация пользователя по паролю. При успехе вернуть JWT access token."""
    q = await db.execute(__import__("sqlalchemy").select(User).where(User.email == form_data.username))
    user = q.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(subject=str(user.id))
    return {"access_token": access}
