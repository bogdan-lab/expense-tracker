import unittest
from datetime import date
from GroupedTransactions import GroupedTransactions
from Categories import Category, Groceries
from ReportParsers import Transaction

class TestTransactionGrouping(unittest.TestCase):
    def setUp(self):
        self.tx_groceries = Transaction(
            account_number="123456789",
            currency="EUR",
            date=date(2025, 1, 1),
            balance_before=100.0,
            balance_after=90.0,
            amount=-12.34,
            description="Payment to Albert Heijn"
        )
        self.tx_other = Transaction(
            account_number="123456789",
            currency="EUR",
            date=date(2025, 1, 2),
            balance_before=90.0,
            balance_after=80.0,
            amount=-56.78,
            description="Payment to Gamma"
        )
        self.tx_refund = Transaction(
            account_number="123456789",
            currency="EUR",
            date=date(2025, 1, 4),
            balance_before=70.0,
            balance_after=80.0,
            amount=8.00,
            description="Refund from Albert Heijn"
        )

    def test_grouping_correctly_sorts_transactions(self):
        class NotGroceries(Category):
            def __init__(self):
                super().__init__('NotGroceries')
            def is_matched(self, tx):
                return not Groceries().is_matched(tx)
        
        grouped = GroupedTransactions(Groceries(), NotGroceries())
        ungrouped = grouped.add_transactions([self.tx_groceries, self.tx_other])
        self.assertEqual(ungrouped, [])

        groceries = [cat for cat in grouped.get_categories() if cat.get_name() == 'Groceries'][0]
        not_groceries = [cat for cat in grouped.get_categories() if cat.get_name() == 'NotGroceries'][0]

        self.assertEqual(len(groceries.get_transactions()), 1)
        self.assertEqual(len(not_groceries.get_transactions()), 1)
        self.assertAlmostEqual(groceries.get_total(), -12.34)
        self.assertAlmostEqual(not_groceries.get_total(), -56.78)

    def test_transaction_matching_multiple_categories_raises(self):
        class MatchEverything(Category):
            def __init__(self, name): super().__init__(name)
            def is_matched(self, tx): return True

        grouped = GroupedTransactions(
            MatchEverything("CatA"),
            MatchEverything("CatB")
        )
        with self.assertRaises(ValueError) as ctx:
            grouped.add_transactions([self.tx_other])
        self.assertIn("matched multiple categories", str(ctx.exception))
        self.assertIn("CatA", str(ctx.exception))
        self.assertIn("CatB", str(ctx.exception))

    def test_transaction_matching_no_category_returns_ungrouped(self):
        class NoMatchCategory(Category):
            def __init__(self): super().__init__('NoMatch')
            def is_matched(self, tx): return False

        grouped = GroupedTransactions(NoMatchCategory())
        ungrouped = grouped.add_transactions([self.tx_other])  
        self.assertEqual(len(ungrouped), 1)  
        self.assertEqual(ungrouped[0], self.tx_other)  

    def test_positive_and_negative_in_same_category(self):
        grouped = GroupedTransactions(Groceries())
        ungrouped = grouped.add_transactions([self.tx_groceries, self.tx_refund])  
        self.assertEqual(ungrouped, [])  

        groceries = grouped.get_categories()[0]
        self.assertEqual(len(groceries.get_transactions()), 2)
        self.assertAlmostEqual(groceries.get_total(), -4.34)

if __name__ == '__main__':
    unittest.main()
