class ExpenseNotFoundError(Exception):
    def __init__(self, expense_id: int):
        super().__init__(f"Expense {expense_id} not found.")
        self.expense_id = expense_id