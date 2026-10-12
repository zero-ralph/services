from typing import Annotated, Callable

from fastapi import Depends

from api.repository.expense import ExpenseRepository
from api.service.expense import ExpenseService

class ExpenseRouter:
    def __init__(self, service: Callable[[ExpenseRepository], ExpenseService]):
        SERVICE = Annotated[ExpenseService, Depends(service)]

        