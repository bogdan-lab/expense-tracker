import unittest
from tempfile import NamedTemporaryFile
from datetime import date
from typing import List
from ReportParsers import parse_transactions

def create_temp_file(lines: List[str]) -> str:
    with NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write('\n'.join(lines) + '\n')
        return tmp.name

class TestParseTransactions(unittest.TestCase):
    def test_valid_transaction_parsing(self):
        lines = [
            "119747944 EUR 20250103 388,30 394,60 20250103 6,30 "
            "SEPA Overboeking IBAN: NL92ADYB2017400998 BIC: ADYBNL2AXXX Naam: Albert Heijn"
        ]
        tmp_path = create_temp_file(lines)
        result = parse_transactions(tmp_path)
        self.assertEqual(len(result), 1)
        tx = result[0]
        self.assertEqual(tx.account_number, "119747944")
        self.assertEqual(tx.currency, "EUR")
        self.assertEqual(tx.date, date(2025, 1, 3))
        self.assertAlmostEqual(tx.balance_before, 388.30)
        self.assertAlmostEqual(tx.balance_after, 394.60)
        self.assertAlmostEqual(tx.amount, 6.30)
        self.assertIn("Albert Heijn", tx.description)

    def test_invalid_row_raises_exception(self):
        lines = ["119747944 EUR 20250103 388,30"]
        tmp_path = create_temp_file(lines)
        with self.assertRaises(ValueError) as context:
            parse_transactions(tmp_path)
        self.assertIn("Invalid transaction row", str(context.exception))

    def test_invalid_date_format_raises_exception(self):
        lines = [
            "119747944 EUR 2025-01-03 388,30 394,60 20250103 6,30 Description"
        ]
        tmp_path = create_temp_file(lines)
        with self.assertRaises(ValueError) as context:
            parse_transactions(tmp_path)
        self.assertIn("Invalid date format", str(context.exception))

if __name__ == '__main__':
    unittest.main()
