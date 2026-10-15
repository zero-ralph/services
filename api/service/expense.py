from api.repository.expense import ExpenseRepository
from core.exceptions import ExpenseNotFoundError
from models.expense import Expense
from schemas.expense import ExpenseCreate


class ExpenseService:
    def __init__(self, repository: ExpenseRepository, logger):
        self.repository = repository
        self.logger = logger

    async def create(self, expense_create_form: ExpenseCreate) -> Expense:
        return await self.repository.create(Expense(**expense_create_form.model_dump()))

    async def get_all(self) -> list[Expense]:
        return await self.repository.get_all()
    
    async def get_by_id(self, expense_id: int) -> Expense:
        expense = await self.repository.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(expense_id)
        return expense
    
    async def update(self, data: ExpenseCreate, expense_id: int) -> Expense:
        expense = await self.get_by_id(expense_id)

        for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(expense, field, value)
        
        return await self.repository.update(expense)

    async def delete(self, expense_id: int) -> None:
        expense = await self.get_by_id(expense_id=expense_id)
        await self.repository.delete(expense)