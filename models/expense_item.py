from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, Boolean, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.expense import Expense

class ExpenseItem(Base):

    __tablename__ = "expense_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE"),
        index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1"))
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())

    expense: Mapped[Expense] = relationship(back_populates="items")
