import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from tests.base import DatabaseTestCase
from api.repository.expense import ExpenseRepository
from models.expense import Expense
from models.expense_item import ExpenseItem


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


    async def test_create_saves_items(self):
        expense = Expense(vendor="Metrobank", total_amount=Decimal("2.00"), duration=2, items=[
            ExpenseItem(amount=Decimal("1.00")),
            ExpenseItem(amount=Decimal("1.00")),
        ])

        created = await self.repository.create(expense)

        self.assertEqual(len(created.items), 2)
        self.assertTrue(all(item.id is not None for item in created.items))
        self.assertTrue(all(item.is_paid is False for item in created.items))

    async def test_get_all_loads_items(self):
        await self.repository.create(Expense(vendor="Metrobank", total_amount=Decimal("3.00"), duration=3, items=[
            ExpenseItem(amount=Decimal("1.00")) for _ in range(3)
        ]))

        expenses = await self.repository.get_all()

        self.assertEqual(len(expenses[0].items), 3)

    async def test_get_all_excludes_deleted(self):
        kept = await self.repository.create(Expense(vendor="BPI", total_amount=Decimal("10.00"), duration=1))
        deleted = await self.repository.create(Expense(vendor="Metrobank", total_amount=Decimal("10.00"), duration=1))
        await self.repository.delete(deleted)

        expenses = await self.repository.get_all()

        self.assertEqual([e.id for e in expenses], [kept.id])

    async def test_get_by_id(self):
        created = await self.repository.create(Expense(vendor="Metrobank", total_amount=Decimal("2.00"), duration=2, items=[
            ExpenseItem(amount=Decimal("1.00")),
            ExpenseItem(amount=Decimal("1.00")),
        ]))

        found = await self.repository.get_by_id(created.id)

        self.assertEqual(found.id, created.id)
        self.assertEqual(len(found.items), 2)

    async def test_get_by_id_not_found(self):
        self.assertIsNone(await self.repository.get_by_id(999999))

    async def test_update_keeps_items(self):
        expense = await self.repository.create(Expense(vendor="Metrobank", total_amount=Decimal("2.00"), duration=2, items=[
            ExpenseItem(amount=Decimal("1.00")),
            ExpenseItem(amount=Decimal("1.00")),
        ]))

        expense.vendor = "BPI"
        updated = await self.repository.update(expense)

        self.assertEqual(len(updated.items), 2)