import redis.asyncio as redis
import json
from core.config import settings
from schemas.order import OrderOut
from typing import Any

class RedisClient:
    def __init__(self):
        self._client: redis.Redis | None = None
        self._ttl = 300

    async def init(self):
        """Инициализация Redis клиента по URL из настроек."""
        self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        """Закрыть соединение с Redis, если оно существует."""
        if self._client:
            await self._client.close()

    async def get_order(self, order_id: str) -> Any | None:
        """Получить заказ из Redis по ключу order:{id} и распарсить JSON, либо вернуть None."""
        if not self._client:
            return None
        data = await self._client.get(f"order:{order_id}")
        if not data:
            return None
        return json.loads(data)

    async def set_order(self, order) -> None:
        """Сохранить представление заказа в Redis (setex) — принимает ORM-объект или словарь."""
        if not self._client:
            return
        # order might be ORM object or dict
        if hasattr(order, "__dict__"):
            payload = {
                "id": str(order.id),
                "user_id": order.user_id,
                "items": order.items,
                "total_price": order.total_price,
                "status": order.status.value if hasattr(order.status, "value") else str(order.status),
                "created_at": order.created_at.isoformat()
            }
        else:
            payload = order
        await self._client.setex(f"order:{payload['id']}", self._ttl, json.dumps(payload))


redis_client = RedisClient()
