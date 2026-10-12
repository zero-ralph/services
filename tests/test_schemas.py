import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import ValidationError
from models.expense import Expense
from schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseRead


class SchemaTestCase(unittest.TestCase):
    def assertValidationError(
        self, 
        schema, 
        data: dict, 
        field: str,
        error_type: str):
        with self.assertRaises(ValidationError) as ctx:
            schema(**data)
        errors = [(e["loc"], e["type"]) for e in ctx.exception.errors()]
        
        self.assertIn(((field,), error_type), errors)


class TestExpenseCreate(SchemaTestCase):

    def valid_data(self, **overrides) -> dict:
        data = {
            "vendor": "Metrobank", 
            "total_amount": "1000.50"
        }
        data.update(overrides)
        return data

    def test_valid(self):
        expense = ExpenseCreate(**self.valid_data())
        self.assertEqual(expense.vendor, "Metrobank")
        self.assertEqual(expense.total_amount, Decimal("1000.50"))

    def test_vendor_is_required(self):
        data = self.valid_data()
        data.pop("vendor")
        self.assertValidationError(ExpenseCreate, data, "vendor", "missing")
 
    def test_vendor_cannot_be_empty(self):
        self.assertValidationError(ExpenseCreate, self.valid_data(vendor=""), "vendor", "string_too_short")

    def test_vendor_max_length(self):
        self.assertValidationError(ExpenseCreate, self.valid_data(vendor="x" * 101), "vendor", "string_too_long")

    def test_total_amount_must_be_positive(self):
        self.assertValidationError(ExpenseCreate, self.valid_data(total_amount=0), "total_amount", "greater_than")

    def test_total_amount_max_two_decimals(self):
        self.assertValidationError(ExpenseCreate, self.valid_data(total_amount="1.234"), "total_amount", "decimal_max_places")

    def test_total_amount_must_be_a_number(self):
        self.assertValidationError(ExpenseCreate, self.valid_data(total_amount="abc"), "total_amount", "decimal_parsing")



class TestExpenseUpdate(SchemaTestCase):

    def test_is_completed_is_required(self):
        expense = ExpenseUpdate()
        self.assertEqual(expense.model_dump(), {'is_completed': False})


class TestExpenseRead(SchemaTestCase):

    def test_from_orm_object(self):
        expense = Expense(
            id=1,
            vendor="Metrobank",
            total_amount=Decimal("1000.50"),
            is_completed=False,
            created_at=datetime(2026, 10, 12, tzinfo=timezone.utc),
            updated_at=None
        )

        read = ExpenseRead.model_validate(expense)

        self.assertEqual(read.id, expense.id)
        self.assertEqual(read.vendor, expense.vendor)
        self.assertEqual(read.total_amount, expense.total_amount)
        self.assertEqual(read.is_completed, False)
        self.assertIsNotNone(read.created_at)
        self.assertIsNone(read.updated_at)