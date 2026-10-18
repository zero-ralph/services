from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Numeric,
    String,
    func,
    false,
    Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.expense_item import ExpenseItem


class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(primary_key=True)
    vendor: Mapped[str] = mapped_column(String(100))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2)) 
    duration: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    items: Mapped[list[ExpenseItem]] = relationship(
        back_populates="expense",
        cascade="all, delete-orphan",
        lazy="raise",
        order_by="ExpenseItem.id"
    )


    def soft_delete(self) -> None:
        self.deleted_at = func.now()
