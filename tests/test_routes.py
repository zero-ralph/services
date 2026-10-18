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
        self.payload = {
            'vendor': 'Metrobank',
            'total_amount': "2000",
            'duration': 6
        }

    async def asyncTearDown(self):
        await self.client.aclose()
        app.dependency_overrides.clear()
        await super().asyncTearDown()

    async def create_expense(self, **overrides) -> dict:
        self.payload.update(overrides)
        response = await self.client.post("/expense", json=self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.json()
    
    async def test_create_route(self):
        response = await self.client.post('/expense', json=self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['vendor'], "Metrobank")
        self.assertEqual(response.json()['total_amount'], "2000.00")
        self.assertFalse(response.json()['is_completed'])


    async def test_create_missing_payload_vendor(self):
        del self.payload['vendor']
        response = await self.client.post('/expense', json=self.payload)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_CONTENT)
        errors = [(e['loc'], e['type']) for e in response.json()['detail']]
        self.assertIn((["body", "vendor"], "missing"), errors)

    async def test_create_missing_payload_total_amount(self):
        del self.payload['total_amount']
        response = await self.client.post('/expense', json=self.payload)
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_CONTENT)
        errors = [(e['loc'], e['type']) for e in response.json()['detail']]
        self.assertIn((["body", "total_amount"], "missing"), errors)

    async def test_get_all(self):        
        await self.create_expense(vendor="BPI")
        await self.create_expense(vendor="Metrobank")

        response = await self.client.get('/expense')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([e["vendor"] for e in response.json()], ["BPI", "Metrobank"])

    async def test_get_by_valid_id(self):
        created = await self.create_expense()

        response = await self.client.get(f"/expense/{created['id']}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['vendor'], created['vendor'])

    
    async def test_get_by_invalid_id(self):
        created = await self.create_expense()

        response = await self.client.get('/expense/999999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_update(self):
        created = await self.create_expense()

        self.payload['vendor'] = "BPI"
        response = await self.client.put(f'/expense/{created['id']}', json=self.payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['vendor'], "BPI")

    async def test_update_invalid_id(self):
        create = await self.create_expense()

        response = await self.client.put(f'/expense/999999', json=self.payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    async def test_delete(self):
        created = await self.create_expense()

        response = await self.client.delete(f"/expense/{created['id']}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    async def test_delete_invalid_id(self):
        response = await self.client.delete(f"/expense/999999")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['detail'], f"Expense 999999 not found.")