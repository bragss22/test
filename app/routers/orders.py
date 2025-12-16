from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from db.session import get_session
from repos.order_repo import OrderRepository
from services.order_service import OrderService
from schemas.order import OrderCreate, OrderOut, OrderUpdate
from jose import jwt
from core.config import settings

oauth2 = OAuth2PasswordBearer(tokenUrl="/token/")

router = APIRouter()


async def get_current_user_id(token: str = Depends(oauth2)):
    """Декодировать токен и вернуть идентификатор пользователя (sub). В случае ошибки — бросить 401."""
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(data.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(payload: OrderCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_session)):
    """Создать новый заказ для текущего пользователя."""
    repo = OrderRepository(db)
    svc = OrderService(repo)
    order = await svc.create_order(user_id, payload)
    return order


@router.get("/{order_id}/", response_model=OrderOut)
async def get_order(order_id: UUID, db: AsyncSession = Depends(get_session)):
    """Получить заказ по его UUID. Если не найден — вернуть 404."""
    repo = OrderRepository(db)
    svc = OrderService(repo)
    order = await svc.get_order(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.patch("/{order_id}/", response_model=OrderOut)
async def update_order(order_id: UUID, payload: OrderUpdate, db: AsyncSession = Depends(get_session)):
    """Обновить статус заказа по его UUID."""
    repo = OrderRepository(db)
    svc = OrderService(repo)
    order = await svc.update_status(order_id, payload.status)
    if not order:
        raise HTTPException(404, "Order not found")
    return order

@router.get("/user/{user_id}/", response_model=List[OrderOut])
async def list_user_orders(user_id: int, db: AsyncSession = Depends(get_session)):
    """Получить список заказов для конкретного пользователя."""
    repo = OrderRepository(db)
    svc = OrderService(repo)
    return await svc.list_by_user(user_id)
