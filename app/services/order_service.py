from messaging.producer import MessagingProducer
from repos.order_repo import OrderRepository
from models.order import Order
from schemas.order import OrderCreate
import logging
from cache.redis import redis_client
from uuid import UUID

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, repo: OrderRepository):
        """Инициализация сервиса заказов с заданным репозиторием."""
        self.repo = repo

    async def create_order(self, user_id: int, payload: OrderCreate) -> Order:
        """Создать заказ в БД, опубликовать событие о новом заказе и положить заказ в кэш."""
        order = Order(user_id=user_id, items=payload.items, total_price=payload.total_price)
        order = await self.repo.create(order)
        order = await self.repo.create(order)
        order_data = {
            "order_id": str(order.id),
            "user_id": user_id,
            "items": payload.items,
            "total_price": payload.total_price,
            "status": "pending"
        }

        try:
            # Используем producer
            await MessagingProducer.publish(routing_key="orders", message=order_data)
            logger.info(f"Сообщение отправлено в очередь 'orders': {order_data['order_id']}")
        except Exception as e:
            logger.error(f"Ошибка отправки в RabbitMQ: {e}")

        await redis_client.set_order(order)
        return order

    async def get_order(self, order_id: UUID):
        """Получить заказ по ID: сначала пытаемся получить из кэша, иначе из репозитория и затем кэшируем."""
        # try cache
        cached = await redis_client.get_order(str(order_id))
        if cached:
            return cached
        order = await self.repo.get(order_id)
        if order:
            await redis_client.set_order(order)
        return order

    async def update_status(self, order_id: UUID, status):
        """Обновить статус заказа в репозитории и при успешном обновлении обновить кэш."""
        order = await self.repo.update_status(order_id, status)
        if order:
            await redis_client.set_order(order)
        return order

    async def list_by_user(self, user_id: int):
        """Вернуть список заказов для заданного пользователя (по user_id)."""
        return await self.repo.list_by_user(user_id)
