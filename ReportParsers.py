from collections import namedtuple
from datetime import datetime, date
from typing import List, Tuple
import re
import csv
import os

Transaction = namedtuple('Transaction', [
    'sender',
    'receiver',
    'currency',
    'date',
    'amount',
    'raw'
])

def parse_float(value: str) -> float:
    return float(value.replace(',', '.'))

def parse_filename(file_path: str) -> Tuple[str, str]:
    """
    Extracts bank name and account owner from a full file path.
    Returns both values in lowercase.
    Expected filename format: '<bank>_<owner>_<...>.ext'
    """
    filename = os.path.basename(file_path)
    match = re.search(r'([^_/\\]+)_([^_/\\]+)_.+\.\w+$', filename)
    if not match:
        raise ValueError(f"Filename '{filename}' does not match expected format '<bank>_<owner>_<...>.ext'")
    return match.group(1).lower(), match.group(2).lower()


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


def parse_ing_transactions(file_path: str) -> List[Transaction]:
    transactions = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)

        if "EUR" not in headers[6]:
            raise ValueError(f"Unexpected currency header: {headers[6]}")

        for row in reader:
            date_str = row[0].strip()
            try:
                tx_date: date = datetime.strptime(date_str, "%Y%m%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format in ING row: {';'.join(row)}")

            account_number = row[2].strip()
            currency = "EUR"

            direction = row[5].strip()
            if direction == "Debit":
                amount = -parse_float(row[6])
            elif direction == "Credit":
                amount = parse_float(row[6])
            else:
                raise ValueError(f"Unknown transaction direction in row: {';'.join(row)}")

            description = row[8].strip()

            transactions.append(Transaction(
                account_number,
                currency,
                tx_date,
                None,
                None,
                amount,
                description
            ))

    return transactions


def parse_revolut_transactions(file_path: str) -> List[Transaction]:
    transactions = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)

        for row in reader:
            date_str = row[2].strip().split()[0]
            try:
                tx_date: date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format in Revolut row: {','.join(row)}")

            account_number = None
            currency = row[7].strip()
            amount = parse_float(row[5])
            description = row[4].strip()

            transactions.append(Transaction(
                account_number,
                currency,
                tx_date,
                None,
                None,
                amount,
                description
            ))

    return transactions
