from celery import Celery
import time
import os

broker = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq//")
backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery("worker", broker=broker, backend=backend)

celery_app.conf.update(
    # Сериализация
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Таймзона
    timezone="UTC",
    enable_utc=True,

    # Настройки подключения к RabbitMQ
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=100,

    # Heartbeat для поддержания соединения
    broker_heartbeat=10,
    broker_connection_timeout=30,

    # Настройки воркера
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,

    # Настройки результатов
    result_expires=3600,
    result_persistent=True,

    # Настройки retry
    task_default_retry_delay=300,
    task_max_retries=3,

    # ЯВНО УКАЗЫВАЕМ ОЧЕРЕДИ
    task_default_queue="celery",
    task_queues={
        "celery": {
            "exchange": "celery",
            "exchange_type": "direct",
            "routing_key": "celery"
        },
        "orders": {
            "exchange": "celery",
            "exchange_type": "direct",
            "routing_key": "orders"
        }
    },

    # Роутинг задач
    task_routes={
        "process_order": {"queue": "orders"},
    },
)


@celery_app.task(name="process_order")
def process_order(order_data: dict):
    """Фоновая задача Celery для обработки заказа (имитация работы через sleep)."""
    time.sleep(2)
    order_id = order_data.get("order_id")
    print(f"Order {order_id} Задача выполнена")
    return {"order_id": order_id, "status": "processed"}
