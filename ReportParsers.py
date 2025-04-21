from collections import namedtuple
from datetime import datetime, date
from typing import List

Transaction = namedtuple('Transaction', [
    'account_number',
    'currency',
    'date',
    'balance_before',
    'balance_after',
    'amount',
    'description'
])

def parse_float(value: str) -> float:
    return float(value.replace(',', '.'))

def parse_abn_amro_transactions(file_path: str) -> List[Transaction]:
    transactions = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 8:
                raise ValueError(f"Invalid transaction row: {line.strip()}")
            account_number = parts[0]
            currency = parts[1]
            try:
                date_parsed: date = datetime.strptime(parts[2], "%Y%m%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format in row: {line.strip()}")
            balance_before = parse_float(parts[3])
            balance_after = parse_float(parts[4])
            amount = parse_float(parts[6])
            description = ' '.join(parts[7:])
            transactions.append(Transaction(
                account_number,
                currency,
                date_parsed,
                balance_before,
                balance_after,
                amount,
                description
            ))
    return transactions
