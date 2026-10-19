import logging
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock

from api.service.expense import ExpenseService
from core.exceptions import ExpenseNotFoundError
from models.expense import Expense
from schemas.expense import ExpenseCreate


class TestExpenseService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.repository = AsyncMock()
        self.repository.create.side_effect = lambda expense: expense
        self.repository.update.side_effect = lambda expense: expense
        self.service = ExpenseService(self.repository, logging.getLogger("test"))

    async def test_create(self):
        data = ExpenseCreate(vendor="Metrobank", total_amount=Decimal("10.00"), duration=6)

        created = await self.service.create(data)

        self.repository.create.assert_awaited_once()
        sent = self.repository.create.await_args.args[0]
        self.assertIsInstance(sent, Expense)
        self.assertEqual(sent.vendor, "Metrobank")
        self.assertEqual(sent.total_amount, Decimal("10.00"))
        self.assertEqual(sent.duration, 6)

        self.assertIs(created, sent)

    async def test_get_all(self):
        expenses = [
            Expense(id=1, vendor="BPI", total_amount=Decimal("10.00")),
            Expense(id=2, vendor="Metrobank", total_amount=Decimal("10.00"))
        ]

        self.repository.get_all.return_value = expenses

        result = await self.service.get_all()

        self.repository.get_all.assert_awaited_once_with()
        self.assertEqual([expense.vendor for expense in expenses], ['BPI', 'Metrobank'])

    async def test_get_by_id(self):
        expense = Expense(id=1, vendor="Metrobank", total_amount=Decimal('10.00'))

        self.repository.get_by_id.return_value = expense

        result = await self.service.get_by_id(1)

        self.repository.get_by_id.assert_awaited_once_with(1)
        self.assertEqual(expense.vendor, "Metrobank")
        self.assertFalse(expense.is_completed)

    async def test_update(self):
        expense = Expense(id=1, vendor="Metrobank", total_amount=Decimal('10.00'), duration=6)
        self.repository.get_by_id.return_value = expense
        self.repository.update.side_effect = lambda e: e

        data = ExpenseCreate(id=1, vendor="BPI", total_amount=Decimal("10.00"), duration=6)
        result = await self.service.update(data=data, expense_id=expense.id)

        self.repository.get_by_id.assert_awaited_once_with(1)
        self.repository.update.assert_awaited_once_with(expense)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.vendor, "BPI")
        self.assertEqual(result.total_amount, Decimal("10.00"))

    async def test_delete(self):
        self.repository.get_by_id.return_value = None

        with self.assertRaises(ExpenseNotFoundError):
            await self.service.delete(expense_id=1)
        
        self.repository.delete.assert_not_awaited()

    async def test_get_by_id_not_found(self):
        self.repository.get_by_id.return_value = None

        with self.assertRaises(ExpenseNotFoundError):
            await self.service.get_by_id(1)

    async def test_update_not_found(self):
        self.repository.get_by_id.return_value = None

        data = ExpenseCreate(vendor="BPI", total_amount=Decimal("10.00"), duration=6)
        with self.assertRaises(ExpenseNotFoundError):
            await self.service.update(data=data, expense_id=1)

        self.repository.update.assert_not_awaited()

    async def test_create_splits_total_into_items(self):
        data = ExpenseCreate(vendor="Metrobank", total_amount=Decimal("12.00"), duration=6)

        created = await self.service.create(data)

        self.assertEqual([i.amount for i in created.items], [Decimal("2.00")] * 6)

    async def test_create_spreads_remainder_over_first_items(self):
        data = ExpenseCreate(vendor="Metrobank", total_amount=Decimal("10.00"), duration=6)

        created = await self.service.create(data)

        self.assertEqual(
            [i.amount for i in created.items],
            [Decimal("1.67")] * 4 + [Decimal("1.66")] * 2,
        )

    async def test_create_items_add_up_to_total(self):
        data = ExpenseCreate(vendor="Metrobank", total_amount=Decimal("1000.01"), duration=7)

        created = await self.service.create(data)

        self.assertEqual(len(created.items), 7)
        self.assertEqual(sum(i.amount for i in created.items), Decimal("1000.01"))

    async def test_create_with_duration_one(self):
        data = ExpenseCreate(vendor="Metrobank", total_amount=Decimal("10.00"), duration=1)

        created = await self.service.create(data)

        self.assertEqual([i.amount for i in created.items], [Decimal("10.00")])





