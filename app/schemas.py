from enum import Enum
from pydantic import BaseModel, Field


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderCreate(BaseModel):
    user_id: int = Field(gt=0)
    symbol: str = Field(min_length=1, max_length=30)
    side: Side
    price: float = Field(gt=0)
    quantity: float = Field(gt=0)
