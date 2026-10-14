from api.repository.expense import ExpenseRepository
from models.expense import Expense
from schemas.expense import ExpenseCreate

class ExpenseService:
    def __init__(self, repository: ExpenseRepository, logger):
        self.repository = repository
        self.logger = logger

    async def create(self, expense_create_form: ExpenseCreate) -> Expense:
        return await self.repository.create(Expense(**expense_create_form.model_dump()))