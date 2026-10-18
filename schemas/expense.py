from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from schemas import ReadModelMixin



class ExpenseItemRead(ReadModelMixin):
    id: int
    amount: Decimal
    is_paid: bool


class ExpenseItemUpdate(BaseModel):
    is_paid: bool


class ExpenseCreate(BaseModel):
    vendor: str = Field(min_length=1, max_length=100)
    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    duration: int = Field(ge=1)


class ExpenseUpdate(BaseModel):
    is_completed: bool = Field(default=False)


class ExpenseRead(ReadModelMixin):
    id: int
    vendor: str
    total_amount: Decimal
    is_completed: bool
    created_at: datetime
    updated_at: datetime | None 
    items: list[ExpenseItemRead]
