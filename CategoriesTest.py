import unittest
from datetime import date
from Categories import Groceries, NotGroceries
from ReportParsers import Transaction

class TestCategoryMatching(unittest.TestCase):
    def setUp(self):
        self.tx_ah = Transaction(
            account_number="123",
            currency="EUR",
            date=date(2025, 1, 1),
            balance_before=100.0,
            balance_after=90.0,
            amount=-10.0,
            description="Albert Heijn purchase"
        )
        self.tx_non_ah = Transaction(
            account_number="123",
            currency="EUR",
            date=date(2025, 1, 1),
            balance_before=90.0,
            balance_after=80.0,
            amount=-10.0,
            description="Payment to Gamma"
        )

    def test_groceries_matches_albert_heijn(self):
        category = Groceries()
        self.assertTrue(category.is_matched(self.tx_ah))
        self.assertFalse(category.is_matched(self.tx_non_ah))

    def test_not_groceries_excludes_albert_heijn(self):
        category = NotGroceries()
        self.assertFalse(category.is_matched(self.tx_ah))
        self.assertTrue(category.is_matched(self.tx_non_ah))

if __name__ == '__main__':
    unittest.main()
