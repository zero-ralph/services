from fastapi import APIRouter, Response, status
from core.database import check_database_connection

class SystemRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/system", tags=["system"])
    
        @self.router.get("/healthz", tags=["system"])
        async def healthz() -> dict[str, str]:
            return {"system": "online"}

        @self.router.get("/healthz/db", tags=["system"])
        async def healthz_db(response: Response) -> dict[str, str]:
            if await check_database_connection():
                return {"database": "is running"}
        
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {'database': "is not running"}