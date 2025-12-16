from pydantic import BaseModel
from typing import List, Any, Optional
from uuid import UUID
from datetime import datetime
from models.order import OrderStatus


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

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    status: OrderStatus
