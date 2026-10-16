import unittest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from fastapi import status
from fastapi.testclient import TestClient
from core.database import check_database_connection, engine
from main import app


class TestHealth(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()
        await engine.dispose()

    async def test_health(self):
        response = await self.client.get('/system/healthz')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"system": "online"})

    async def test_database(self):
        response = await self.client.get('/system/healthz/db')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'database': 'is running'})

    async def test_if_app_can_connect_to_database(self):
        self.assertTrue(await check_database_connection())

    async def test_database_down_returns_503(self):
        with patch("api.routes.system.check_database_connection", AsyncMock(return_value=False)):
            response = await self.client.get("/system/healthz/db")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.json(), {"database": "is not running"})