import logging
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock

from api.service.expense import ExpenseService
from models.expense import Expense
from schemas.expense import ExpenseCreate


class TestExpenseService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.repository = AsyncMock()
        self.repository.create.side_effect = lambda expense: expense
        self.service = ExpenseService(self.repository, logging.getLogger("test"))

    async def test_create(self):
        data = ExpenseCreate(vendor="Metrobank", total_amount=Decimal("10.00"))

        created = await self.service.create(data)

        self.repository.create.assert_awaited_once()
        sent = self.repository.create.await_args.args[0]
        self.assertIsInstance(sent, Expense)
        self.assertEqual(sent.vendor, "Metrobank")
        self.assertEqual(sent.total_amount, Decimal("10.00"))

        self.assertIs(created, sent)