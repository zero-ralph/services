import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.routes import system 
from core.config import Settings
from core.logger import configure_logging

settings = Settings()

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app.title} in Version {settings.app.version}")

    yield
    logger.info(f"System Shutting down")

app = FastAPI(
    title=settings.app.title,
    version=settings.app.version,
    description=settings.app.description,
    lifespan=lifespan,
)
app.include_router(system.router)

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        reload=True
    )