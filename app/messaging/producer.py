import aio_pika
import json
import logging
import asyncio
from core.config import settings

logger = logging.getLogger(__name__)


class MessagingProducer:
    _conn: aio_pika.RobustConnection | None = None
    _channel: aio_pika.RobustChannel | None = None
    _is_connected = False
    _lock = asyncio.Lock()

    @classmethod
    async def connect(cls, url: str = None):
        """Установить устойчивое соединение с RabbitMQ."""
        if url is None:
            url = settings.RABBITMQ_URL

        async with cls._lock:
            try:
                if cls._is_connected and cls._conn and not cls._conn.is_closed:
                    logger.info("Уже подключено к RabbitMQ")
                    return

                logger.info(f"🔗 Подключение к RabbitMQ: {url}")
                cls._conn = await aio_pika.connect_robust(url, timeout=10)
                cls._channel = await cls._conn.channel()
                cls._is_connected = True

                # Объявляем exchange и очередь
                await cls._declare_celery_queue()

                logger.info("Подключение к RabbitMQ успешно")
            except Exception as e:
                logger.error(f"Ошибка подключения к RabbitMQ: {e}")
                cls._is_connected = False
                raise

    @classmethod
    async def _declare_celery_queue(cls):
        """Объявить очередь для Celery."""
        if not cls._channel:
            return

        try:
            # Создаем exchange (идемпотентно)
            exchange = await cls._channel.declare_exchange(
                "celery",
                aio_pika.ExchangeType.DIRECT,
                durable=True,
                auto_delete=False
            )

            # Создаем очередь (идемпотентно)
            queue = await cls._channel.declare_queue(
                "orders",
                durable=True
            )

            # Привязываем очередь к exchange
            await queue.bind(exchange, routing_key="orders")

            logger.info("Очередь 'orders' объявлена для Celery")
        except Exception as e:
            logger.error(f"Ошибка объявления очереди: {e}")
            raise

    @classmethod
    async def _ensure_connected(cls):
        """Убедиться, что соединение активно."""
        if not cls._is_connected or not cls._conn or cls._conn.is_closed:
            logger.warning("Соединение разорвано, переподключаемся...")
            await cls.connect()

    @classmethod
    async def publish(cls, routing_key: str, message: dict):
        """
        Опубликовать сообщение в exchange "celery".
        """
        await cls._ensure_connected()

        if not cls._is_connected:
            logger.error("Не удалось подключиться к RabbitMQ")
            return

        async with cls._lock:
            try:
                # Формируем сообщение в формате Celery
                celery_message = {
                    "task": "process_order",
                    "id": message.get("order_id", "unknown"),
                    "args": [message],
                    "kwargs": {},
                    "retries": 0,
                    "eta": None,
                    "expires": None,
                }

                # Сериализуем
                body = json.dumps(celery_message).encode()

                # Создаем сообщение
                message_obj = aio_pika.Message(
                    body=body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json",
                    content_encoding="utf-8",
                    headers={
                        "lang": "py",
                        "task": "process_order",
                        "id": message.get("order_id", "unknown"),
                        "root_id": message.get("order_id", "unknown"),
                        "parent_id": None,
                        "group": None,
                    }
                )

                # Получаем exchange (идемпотентно)
                exchange = await cls._channel.declare_exchange(
                    "celery",
                    aio_pika.ExchangeType.DIRECT,
                    durable=True,
                    auto_delete=False
                )

                # Публикуем
                await exchange.publish(
                    message_obj,
                    routing_key=routing_key
                )

                logger.info(f"Сообщение отправлено в очередь '{routing_key}': {message.get('order_id')}")
                logger.debug(f"Содержимое: {celery_message}")

            except Exception as e:
                logger.error(f"Ошибка отправки сообщения: {e}")
                # Помечаем соединение как разорванное
                cls._is_connected = False
                raise

    @classmethod
    async def close(cls):
        """Закрыть соединение с RabbitMQ."""
        async with cls._lock:
            if cls._conn:
                await cls._conn.close()
                cls._is_connected = False
                cls._conn = None
                cls._channel = None
                logger.info("Соединение с RabbitMQ закрыто")

    @classmethod
    def is_connected(cls) -> bool:
        """Проверка подключения."""
        return cls._is_connected and cls._conn and not cls._conn.is_closed
