from fastapi import status
from httpx import AsyncClient, ASGITransport
from core.database import get_database
from main import app
from tests.base import DatabaseTestCase


class TestExpenseRoutes(DatabaseTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        app.dependency_overrides[get_database] = lambda: self.session
        self.client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test'
        )

    async def asyncTearDown(self):
        await self.client.aclose()
        app.dependency_overrides.clear()
        await super().asyncTearDown()

    async def create_expense(self, **overrides) -> dict:
        payload = {
            'vendor': 'Metrobank',
            'total_amount': "2000"
        }
        payload.update(overrides)
        response = await self.client.post("/expense", json=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.json()

    async def test_create(self):
        payload = await self.create_expense()

        self.assertIsInstance(payload['id'], int)
        self.assertEqual(payload['vendor'], 'Metrobank')
        self.assertEqual(payload['total_amount'], '2000')
        self.assertFalse(payload['is_completed'])

    async def test_create_missing_payload_vendor(self):
        payload = {
            'total_amount': "2000.00"
        }
        response = await self.client.post('/expense', json=payload)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_CONTENT)
        errors = [(e['loc'], e['type']) for e in response.json()['detail']]
        self.assertIn((["body", "vendor"], "missing"), errors)

    
    async def test_get_all(self):
        await self.create_expense(vendor="BPI")
        await self.create_expense()

        response = await self.client.get('/expense')

        self.assertEqual(response.status, status.HTTP_200_OK)
        self.assertEqual([e["vendor"] for e in response.json()], ["BPI", "Metrobank"])


    async def test_get_by_id(self):
        created = await self.create_expense()

        response = await self.client.get(f"/expense/{created['id']}")

        self.assertEqual(response.json(), status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], created['id'])
        self.assertEqual(response.json()['vendor'], created['vendor'])