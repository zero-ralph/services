import unittest
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from core.database import Base, engine
from models.expense import Expense


class TestExpenseModel(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        Base.metadata.create_all(engine)

    def setUp(self):
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.session = Session(
            bind=self.connection, join_transaction_mode="create_savepoint"
        )
    
    def tearDown(self):
        self.session.close()
        self.transaction.rollback() # This will remove any created data for testing purposes
        # self.transaction.commit() # This will add the create data for checking purposes
        self.connection.close()

    def expense_object(self, exclude_fields: list = None, **overrides) -> Expense:
        data = {
            'vendor': 'Metrobank',
            'total_amount': Decimal("1000.59")
        }
        data.update(overrides)

        if exclude_fields:
            for field in exclude_fields:
                data.pop(field)

        return Expense(**data)
    
    def test_create_expense(self):
        self.session.add(self.expense_object())
        self.session.commit()

        expense = self.session.scalars(select(Expense)).one()

        self.assertIsNotNone(expense.id)
        self.assertEqual(expense.vendor, 'Metrobank')
        self.assertEqual(expense.total_amount, Decimal("1000.59"))
        self.assertIsNotNone(expense.created_at)


    def test_create_expense_vendor_is_required(self):
        expense = self.expense_object(exclude_fields=["vendor"])
        
        self.session.add(expense)
        with self.assertRaises(IntegrityError):
           self.session.flush()

    def test_create_expense_total_amount_is_required(self):
        expense = self.expense_object(exclude_fields=["vendor"])
        
        self.session.add(expense)
        with self.assertRaises(IntegrityError):
           self.session.flush()

    def test_update_expense(self):
        expense = self.expense_object()
        self.session.add(expense)
        self.session.commit()


        expense.vendor = "BPI"
        self.session.commit()

        self.session.expire_all()

        updated_expense = self.session.get(Expense, expense.id)

        self.assertEqual(updated_expense.vendor, "BPI")
        self.assertEqual(updated_expense.total_amount, Decimal("1000.59"))

    def test_soft_delete_expense(self):
        expense = self.expense_object()
        self.session.add(expense)
        self.session.commit()

        expense_id = expense.id

        expense.soft_delete()
        self.session.commit()

        self.session.expire_all()
        self.assertIsNotNone(self.session.get(Expense, expense_id))


        