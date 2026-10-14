from datetime import datetime
from decimal import Decimal
from typing import Annotated, Callable

from fastapi import APIRouter, Depends, status

from api.repository.expense import ExpenseRepository
from api.service.expense import ExpenseService
from schemas.expense import ExpenseRead, ExpenseCreate


class ExpenseRouter:
    def __init__(self, service: Callable[[ExpenseRepository], ExpenseService]):
        self.router = APIRouter(prefix="/expense", tags=['expense'])
        self.service = Annotated[ExpenseService, Depends(service)]

        @self.router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
        async def expense_create(data: ExpenseCreate, service: self.service):
            return await service.create(expense_create_form=data)
        
        # @self.router.get("", response_model=list[ExpenseRead], status_code=status.HTTP_200_OK)
        # async def expense_list(service: SERVICE):
        #     return []

        # @self.router.get("/{expense_id}", response_model=ExpenseRead, status_code=status.HTTP_200_OK)
        # async def expense_get_by_id(service: SERVICE):
        #     pass

        # @self.router.put("/{expense_id}", response_model=ExpenseRead, status_code=status.HTTP_200_OK)
        # async def expense_update(service: SERVICE):
        #     pass

        # @self.router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
        # async def expense_delete(service: SERVICE):
        #     pass

        


    