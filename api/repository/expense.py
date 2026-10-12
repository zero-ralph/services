from sqlalchemy.ext.asyncio import AsyncSession

class ExpenseRepository:
    def __init__(self, session: AsyncSession, logger) -> None:
        self.session = session
        self.logger = logger