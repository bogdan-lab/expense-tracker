from collections import namedtuple
from datetime import datetime, date
from typing import List, Tuple
import re
import csv
import os
import logging


logger = logging.getLogger(__name__)


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


def parse_abn_amro_receiver(raw_description: str) -> str:
    # Normalize spacing and split into parts
    tabbed = re.sub(r'\s{2,}', '\t', raw_description)
    parts = tabbed.split('\t')

    # Case 1: NAME/
    match_name = re.search(r'NAME/([^/]+)', raw_description)
    if match_name:
        return match_name.group(1).strip()

    # Case 2: Naam:
    match_naam = re.search(r'Naam:\s*(.*)', raw_description)
    if match_naam:
        return match_naam.group(1).strip()

    # Case 3: BEA, Betaalpas
    if len(parts) >= 2 and parts[0].strip() == "BEA, Betaalpas":
        bea_match = re.match(r'^(.*?),PAS', parts[1])
        if bea_match:
            return bea_match.group(1).strip()

    # Case 4: eCom, Apple Pay
    if len(parts) >= 2 and parts[0].strip() == "eCom, Apple Pay":
        return parts[1].strip()

    # Case 5: ABN AMRO Bank N.V.
    if parts[0].strip() == "ABN AMRO Bank N.V.":
        return "ABN AMRO Bank N.V."

    raise ValueError(f"Unrecognized receiver format in description: {raw_description}")

def parse_abn_amro_transactions(filepath: str) -> List[Transaction]:
    transactions = []
    sender, _ = parse_filename(filepath)

    with open(filepath, encoding='utf-8') as f:
        for line in f:
            raw = line.strip()
            parts = raw.split('\t')
            
            if len(parts) != 8:
                raise ValueError(f"Invalid row format: {raw}")

            currency = parts[1]

            try:
                date = datetime.strptime(parts[2], "%Y%m%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {raw}")

            try:
                amount = parse_float(parts[6])
            except ValueError:
                raise ValueError(f"Invalid amount: {raw}")

            try:
                receiver = parse_abn_amro_receiver(parts[7])
            except ValueError as e:
                print(f"{e}")
                print(parts[7])
                continue

            transactions.append(Transaction(
                sender=sender,
                receiver=receiver,
                currency=currency,
                date=date,
                amount=amount,
                raw=raw
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
