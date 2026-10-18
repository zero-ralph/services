from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from core.database import Base, engine
from models.expense import Expense
from models.expense_item import ExpenseItem
from tests.base import DatabaseTestCase

class TestExpenseModel(DatabaseTestCase):

    def expense_object(self, exclude_fields: list = None, **overrides) -> Expense:
        data = {
            'vendor': 'Metrobank',
            'total_amount': Decimal("1000.59"),
            'duration': 6
        }
        data.update(overrides)

        if exclude_fields:
            for field in exclude_fields:
                data.pop(field)

        return Expense(**data)

    async def save_object(self, expense: Expense) -> Expense:
        self.session.add(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        return expense
    
    async def test_create_expense(self):
        await self.save_object(self.expense_object())

        expense = (await self.session.scalars(select(Expense))).one()

        self.assertIsNotNone(expense.id)
        self.assertEqual(expense.vendor, 'Metrobank')
        self.assertEqual(expense.total_amount, Decimal("1000.59"))
        self.assertIsNotNone(expense.created_at)


    async def test_create_expense_vendor_is_required(self):
        expense = self.expense_object(exclude_fields=["vendor"])
        
        self.session.add(expense)
        with self.assertRaises(IntegrityError):
           await self.session.flush()

    async def test_create_expense_total_amount_is_required(self):
        expense = self.expense_object(exclude_fields=["total_amount"])
        
        self.session.add(expense)
        with self.assertRaises(IntegrityError):
            await self.session.flush()

    async def test_update_expense(self):
        expense = await self.save_object(self.expense_object())

        expense.vendor = "BPI"
        await self.session.commit()

        await self.session.refresh(expense)


        self.assertEqual(expense.vendor, "BPI")
        self.assertEqual(expense.total_amount, Decimal("1000.59"))

    async def test_soft_delete_expense(self):
        expense = await self.save_object(self.expense_object())
        
        expense_id = expense.id

        expense.soft_delete()
        await self.session.commit()

        await self.session.refresh(expense)
        self.assertIsNotNone(await self.session.get(Expense, expense_id))




class TestExpenseItemModel(DatabaseTestCase):

    async def save(self, obj):
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def load_expense(self, expense_id: int) -> Expense:
        self.session.expunge_all()
        return (await self.session.scalars(
            select(Expense).where(Expense.id == expense_id).options(selectinload(Expense.items))
        )).one()

    async def test_expense_with_items(self):
        expense = Expense(vendor="Metrobank", total_amount=Decimal("10.00"), items=[
            ExpenseItem(amount=Decimal("1.00"))
        ])

        await self.save(expense)

        loaded = await self.load_expense(expense.id)

        self.assertEqual([i.amount for i in loaded.items], [Decimal("1.00")])
        self.assertEqual(loaded.items[0].amount, Decimal("1.00"))

        