import unittest
from fastapi import status
from fastapi.testclient import TestClient
from core.database import check_database_connection, engine
from main import app


class TestHealth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
    
    def test_health(self):
        response = self.client.get('/system/healthz')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"system": "online"})

    def test_database(self):
        response = self.client.get('/system/healthz/db')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'database': 'is running'})

class TestDatabaseConnection(unittest.IsolatedAsyncioTestCase):
    async def test_if_app_can_connect_to_database(self):
        self.assertTrue(await check_database_connection())

    async def asyncTearDown(self):
        await engine.dispose()
