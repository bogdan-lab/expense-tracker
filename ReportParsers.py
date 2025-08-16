from collections import namedtuple
from datetime import datetime, date
from typing import List, Tuple
import re
import csv
import os
import logging


logger = logging.getLogger(__name__)


Transaction = namedtuple('Transaction', [
    'sender_bank',
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
    return (match.group(1), match.group(2))



def parse_abn_amro_receiver(raw_description: str) -> str:
    if raw_description.startswith("BEA, Betaalpas"):
        match = re.search(r"BEA, Betaalpas\s+(.*?),PAS", raw_description)
        if match:
            return match.group(1).strip()
        raise ValueError(f"Could not extract receiver from BEA, Betaalpas description: {raw_description}")

    if raw_description.startswith("SEPA"):
        match = re.search(r"Naam:\s*(.+?)(?:\s{2,}|$)", raw_description)
        if match:
            return match.group(1).strip()
        raise ValueError(f"Could not extract receiver from SEPA description: {raw_description}")

    if raw_description.startswith("/TRTP"):
        match = re.search(r"/NAME/([^/]+)", raw_description)
        if match:
            return match.group(1).strip()
        raise ValueError(f"Could not extract receiver from /TRTP description: {raw_description}")

    if raw_description.startswith("eCom, Apple Pay"):
        columns = re.split(r"\s{2,}", raw_description)
        if len(columns) >= 2:
            return columns[1].strip()
        raise ValueError(f"Could not extract receiver from eCom, Apple Pay description: {raw_description}")

    if raw_description.startswith("ABN AMRO Bank N.V."):
        return "ABN AMRO Bank N.V."

    raise ValueError(f"Unrecognized receiver format: {raw_description}")

def parse_abn_amro_transactions(filepath: str) -> List[Transaction]:
    transactions = []
    bank, sender = parse_filename(filepath)

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
                sender_bank=bank,
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
    bank, sender = parse_filename(file_path)

    with open(file_path, encoding="utf-8") as f:
        csv_delimiter = ';'
        reader = csv.reader(f, delimiter=csv_delimiter)
        headers = next(reader)

        if "EUR" not in headers[6]:
            raise ValueError(f"Unexpected currency header: {headers[6]}")

        for row in reader:
            date_str = row[0].strip()
            try:
                tx_date: date = datetime.strptime(date_str, "%Y%m%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format in ING row: {';'.join(row)}")

            direction = row[5].strip()
            if direction == "Debit":
                amount = -parse_float(row[6])
            elif direction == "Credit":
                amount = parse_float(row[6])
            else:
                raise ValueError(f"Unknown transaction direction in row: {';'.join(row)}")

            description = row[8].strip()

            transactions.append(Transaction(
                sender_bank=bank,
                sender=sender,
                receiver=row[1].strip(),
                currency="EUR",
                date=tx_date,
                amount=amount,
                raw=csv_delimiter.join(row)
            ))


    return transactions


def parse_revolut_transactions(file_path: str) -> List[Transaction]:
    transactions = []
    bank, sender = parse_filename(file_path)

    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            date_str = row[2].strip().split()[0]
            try:
                tx_date: date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format in Revolut row: {','.join(row)}")

            transactions.append(Transaction(
                sender_bank=bank,
                sender=sender,
                receiver=row[4].strip(),
                currency=row[7].strip(),
                date=tx_date,
                amount=parse_float(row[5]),
                raw=','.join(row)
            ))


    return transactions
