from datetime import datetime
from decimal import Decimal
from typing import Annotated, Callable

from fastapi import (
    APIRouter, 
    Depends,
    HTTPException, 
    status
)

from api.repository.expense import ExpenseRepository
from api.service.expense import ExpenseService
from core.exceptions import ExpenseNotFoundError
from schemas.expense import ExpenseRead, ExpenseCreate


class ExpenseRouter:
    def __init__(self, service: Callable[[ExpenseRepository], ExpenseService]):
        self.router = APIRouter(prefix="/expense", tags=['expense'])
        self.service = Annotated[ExpenseService, Depends(service)]

        @self.router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
        async def expense_create(data: ExpenseCreate, service: self.service):
            return await service.create(expense_create_form=data)
        
        @self.router.get("", response_model=list[ExpenseRead], status_code=status.HTTP_200_OK)
        async def expense_list(service: self.service):
            return await service.get_all()

        @self.router.get("/{expense_id}", response_model=ExpenseRead, status_code=status.HTTP_200_OK)
        async def expense_get_by_id(expense_id: int, service: self.service):
            try:
                return await service.get_by_id(expense_id)
            except ExpenseNotFoundError as error:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
            
        @self.router.put("/{expense_id}", response_model=ExpenseRead, status_code=status.HTTP_200_OK)
        async def expense_update(data: ExpenseCreate, expense_id: int, service: self.service):
            try:
                return await service.update(data, expense_id)
            except ExpenseNotFoundError as error:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))

        @self.router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def expense_delete(expense_id: int, service: self.service):
            try:
                await service.delete(expense_id=expense_id)
                return {'detail': "no expense found"}
            except ExpenseNotFoundError as error:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
            

        


    