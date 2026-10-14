import logging
from decimal import Decimal

from sqlalchemy import select

from tests.base import DatabaseTestCase
from api.repository.expense import ExpenseRepository
from models.expense import Expense


class TestExpenseRepository(DatabaseTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.repository = ExpenseRepository(self.session, logging.getLogger("test"))
    
    async def test_create(self):
        expense = Expense(vendor="Metrobank", total_amount=Decimal("10.00"))

        created = await self.repository.create(expense)

        self.assertIsNotNone(created.id)
        self.assertIsNotNone(created.vendor)
        self.assertIsNotNone(created.created_at)
        self.assertFalse(created.is_completed)
        self.assertIsNone(created.updated_at)
        self.assertIsNone(created.deleted_at)

        saved = (await self.session.scalars(select(Expense).where(Expense.id == created.id))).one()

        self.assertEqual(saved.vendor, "Metrobank")
        self.assertEqual(saved.total_amount, Decimal("10.00"))