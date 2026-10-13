import logging
from sqlalchemy import (
    text,
    URL
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool
from core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
    database=settings.database.database
)
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)

SESSION_LOCAL = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    autoflush=False, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


async def check_database_connection() -> bool:
    is_connected = False
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        is_connected = True
    except SQLAlchemyError:
        logger.error("Database connection failed")
        is_connected = False

    return is_connected


async def get_database():
    async with SESSION_LOCAL() as session:
        yield session
    
