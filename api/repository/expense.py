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