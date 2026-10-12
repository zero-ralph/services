import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.repository.expense import ExpenseRepository
from api.routes import system
from api.service.expense import ExpenseService
 
from core.config import Settings
from core.database import check_database_connection, engine, get_database
from core.logger import configure_logging


settings = Settings()

configure_logging()
logger = logging.getLogger(__name__)


# Dependencies
# Expense
def expense_repository_dependencies(
    session: Annotated[AsyncSession, Depends(get_database)]) -> ExpenseRepository:
    return ExpenseRepository(session, logger)

def expense_service_dependencies(
    repository: Annotated[ExpenseRepository, Depends(expense_repository_dependencies)]) -> ExpenseService:
    return ExpenseService(repository, logger)
# End 


# App
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app.title} in Version {settings.app.version}")
    if not await check_database_connection():
        raise RuntimeError("Cannot connect to the database")
    yield
    await engine.dispose()
    logger.info(f"System Shutting down")

app = FastAPI(
    title=settings.app.title,
    version=settings.app.version,
    description=settings.app.description,
    lifespan=lifespan,
)
app.include_router(system.router)
# End 


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        reload=True
    )