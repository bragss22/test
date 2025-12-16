from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.order import Order, OrderStatus
from uuid import UUID

class OrderRepository:
    def __init__(self, db: AsyncSession):
        """Инициализация репозитория с асинхронной сессией БД."""
        self.db = db

    async def create(self, order: Order) -> Order:
        """Добавить новый объект Order в БД и вернуть обновлённый объект."""
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get(self, order_id: UUID) -> Order | None:
        """Получить Order по его UUID или вернуть None, если не найден."""
        q = select(Order).where(Order.id == order_id)
        res = await self.db.execute(q)
        return res.scalars().first()

    async def update_status(self, order_id: UUID, status: OrderStatus) -> Order | None:
        """Обновить статус заказа и вернуть обновлённый объект Order (или None, если не найден)."""
        q = update(Order).where(Order.id == order_id).values(status=status).returning(Order)
        res = await self.db.execute(q)
        await self.db.commit()
        row = res.fetchone()
        return row[0] if row else None

    async def list_by_user(self, user_id: int):
        """Вернуть список заказов пользователя, отсортированных по дате создания (убывание)."""
        q = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        res = await self.db.execute(q)
        return res.scalars().all()
