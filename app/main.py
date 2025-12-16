from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from routers import auth, orders
from core.config import settings
from db.session import async_init_db
from cache.redis import redis_client
from messaging.producer import MessagingProducer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения

    При старте: инициализация БД
    При остановке: очистка ресурсов
    """
    # Инициализация БД при старте
    await async_init_db()
    await redis_client.init()
    await MessagingProducer.connect(settings.RABBITMQ_URL)
    yield
    await redis_client.close()
    await MessagingProducer.close()

app = FastAPI(title="Order Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
