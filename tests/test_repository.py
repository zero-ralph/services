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

    async def test_get_all(self):
        await self.repository.create(Expense(vendor="BPI", total_amount=Decimal("10.00")))
        await self.repository.create(Expense(vendor="Metrobank", total_amount=Decimal("10.00")))

        expenses = await self.repository.get_all()

        self.assertEqual([expense.vendor for expense in expenses], ["BPI", "Metrobank"])
    
    async def test_update(self):
        expense = await self.repository.create(Expense(vendor="Metrobank", total_amount=Decimal("10.00")))
        expense.vendor = "BPI"
        updated = await self.repository.update(expense)

        self.assertEqual(updated.vendor, "BPI")
        self.assertIsNotNone(updated.updated_at)

        saved = (await self.session.scalars(select(Expense).where(Expense.id == expense.id))).one()
        self.assertEqual(saved.vendor, "BPI")

    async def test_delete(self):
        expense = await self.repository.create(Expense(vendor="Metrobank", total_amount=Decimal("10.00")))
        expense_id = expense.id 
        await self.repository.delete(expense=expense)

        row = (await self.session.scalars(select(Expense).where(Expense.id == expense_id))).one()
        self.assertIsNotNone(row.deleted_at)
        self.assertIsNone(await self.repository.get_by_id(expense_id))