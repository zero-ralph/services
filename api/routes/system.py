from fastapi import APIRouter
from core.database import check_database_connection


router = APIRouter(prefix="/system", tags=["system"])

@router.get("/healthz", tags=["healthz"])
def healthz() -> dict[str, str]:
    return {"system": "online"}


@router.get("/healthz/db", tags={"healthz"})
async def healthz_db() -> dict[str, str]:
    is_running = "is not connected"
    if await check_database_connection():
        is_running = "is running"
    return {'database': is_running}