from api.repository.expense import ExpenseRepository

class ExpenseService:
    def __init__(self, repository: ExpenseRepository, logger):
        self.repository = repository
        