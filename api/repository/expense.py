from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.expense import Expense


class ExpenseRepository:
    def __init__(self, session: AsyncSession, logger) -> None:
        self.session = session
        self.logger = logger
    
    async def create(self, expense: Expense) -> Expense:
        self.session.add(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        return expense
    
    async def get_all(self) -> list[Expense]:
        results = await self.session.scalars(
            select(Expense).where(Expense.deleted_at.is_(None)).order_by(Expense.created_at.desc())
        )
        return list(results)

    async def get_by_id(self, expense_id: int) -> Expense:
        result = await self.session.scalars(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.deleted_at.is_(None),
            )
        )
        return result.one_or_none()

    async def update(self, expense: Expense) -> Expense:
        await self.session.commit()
        await self.session.refresh(expense)
        return expense

    async def delete(self, expense: Expense) -> None:
        expense.soft_delete()
        await self.session.commit()
        await self.session.refresh(expense)