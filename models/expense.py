from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    DateTime,
    Numeric,
    String,
    func,
    false
)
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(primary_key=True)
    vendor: Mapped[str] = mapped_column(String(100))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2)) 
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


    def soft_delete(self) -> None:
        self.deleted_at = func.now()
