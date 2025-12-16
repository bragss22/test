from datetime import datetime
from typing import Any, List
from uuid import UUID

from models.order import OrderStatus
from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    items: List[Any]
    total_price: float


class OrderOut(BaseModel):
    id: UUID
    user_id: int
    items: List[Any]
    total_price: float
    status: OrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderUpdate(BaseModel):
    status: OrderStatus
