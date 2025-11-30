from collections import namedtuple
from datetime import datetime, date
from typing import List, Tuple, NamedTuple
import re
import csv
import os
import logging
from enum import Enum
from io import StringIO
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Bank(Enum):
    ABN_AMRO = "ABNAMRO"
    ING = "ING"
    REVOLUT = "Revolut"

    def __lt__(self, other):
        if not isinstance(other, Bank):
            raise RuntimeError(f"Try to compare Bank with {type(other)}")
        return self.value < other.value


@dataclass(frozen=True, order=True)
class Transaction:
    sender_bank: Bank
    sender: str
    receiver: str
    currency: str
    date: date
    amount: float
    raw: str

    def __post_init__(self):
        object.__setattr__(self, "sender", self.sender.lower())
        object.__setattr__(self, "receiver", self.receiver.lower())
        object.__setattr__(self, "currency", self.currency.lower())

    @classmethod
    def from_strings(cls, values: List[str]) -> "Transaction":
        return cls(
            Bank(values[0]),
            values[1],
            values[2],
            values[3],
            datetime.strptime(values[4], "%Y-%m-%d").date(),
            float(values[5]),
            values[6],
        )


def parse_float(value: str) -> float:
    return float(value.replace(",", "."))


def parse_filename(file_path: str) -> Tuple[str, str]:
    """
    Extracts bank name and account owner from a full file path.
    Returns both values in lowercase.
    Expected filename format: '<bank>_<owner>_<...>.ext'
    """
    filename = os.path.basename(file_path)
    match = re.search(r"([^_/\\]+)_([^_/\\]+)_.+\.\w+$", filename)
    if not match:
        raise ValueError(
            f"Filename '{filename}' does not match expected format '<bank>_<owner>_<...>.ext'"
        )
    return (Bank(match.group(1)), match.group(2))


def parse_abn_amro_receiver(raw_description: str) -> str:
    if raw_description.startswith("BEA, Betaalpas"):
        match = re.search(r"BEA, Betaalpas\s+(.*?),PAS", raw_description)
        if match:
            return match.group(1).strip()
        raise ValueError(
            f"Could not extract receiver from BEA, Betaalpas description: {raw_description}"
        )

    if raw_description.startswith("SEPA"):
        match = re.search(r"Naam:\s*(.+?)(?:\s{2,}|$)", raw_description)
        if match:
            return match.group(1).strip()
        raise ValueError(
            f"Could not extract receiver from SEPA description: {raw_description}"
        )

    if raw_description.startswith("/TRTP"):
        match = re.search(r"/NAME/([^/]+)", raw_description)
        if match:
            return match.group(1).strip()
        raise ValueError(
            f"Could not extract receiver from /TRTP description: {raw_description}"
        )

    if raw_description.startswith("eCom, Apple Pay"):
        columns = re.split(r"\s{2,}", raw_description)
        if len(columns) >= 2:
            return columns[1].strip()
        raise ValueError(
            f"Could not extract receiver from eCom, Apple Pay description: {raw_description}"
        )

    if raw_description.startswith("ABN AMRO Bank N.V."):
        return "ABN AMRO Bank N.V."

    raise ValueError(f"Unrecognized receiver format: {raw_description}")


def abn_amro_report_to_transactions(report: StringIO, sender: str) -> List[Transaction]:
    transactions = []
    for line in report:
        raw = line.strip()
        parts = raw.split("\t")

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

        transactions.append(
            Transaction(
                sender_bank=Bank.ABN_AMRO,
                sender=sender,
                receiver=receiver,
                currency=currency,
                date=date,
                amount=amount,
                raw=raw,
            )
        )

    return transactions


def ing_report_to_transactions(report: StringIO, sender: str) -> List[Transaction]:
    transactions = []

    csv_delimiter = ";"
    reader = csv.reader(report, delimiter=csv_delimiter)
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

        transactions.append(
            Transaction(
                sender_bank=Bank.ING,
                sender=sender,
                receiver=row[1].strip(),
                currency="EUR",
                date=tx_date,
                amount=amount,
                raw=csv_delimiter.join(row),
            )
        )

    return transactions


def revolut_report_to_transactions(report: StringIO, sender: str) -> List[Transaction]:
    transactions = []
    reader = csv.reader(report)
    header = next(reader)

    for row in reader:
        date_str = row[2].strip().split()[0]
        try:
            tx_date: date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format in Revolut row: {','.join(row)}")

        transactions.append(
            Transaction(
                sender_bank=Bank.REVOLUT,
                sender=sender,
                receiver=row[4].strip(),
                currency=row[7].strip(),
                date=tx_date,
                amount=parse_float(row[5]),
                raw=",".join(row),
            )
        )

    return transactions


def report_to_transactions(
    report: StringIO, bank: Bank, sender: str
) -> List[Transaction]:
    if bank == Bank.ABN_AMRO:
        return abn_amro_report_to_transactions(report, sender)
    elif bank == Bank.ING:
        return ing_report_to_transactions(report, sender)
    elif bank == Bank.REVOLUT:
        return revolut_report_to_transactions(report, sender)
    else:
        raise ValueError(f"Unknown bank: {bank}")


def transactions_from_file(file_path: str) -> List[Transaction]:
    assert os.path.isfile(file_path)
    filename = os.path.basename(file_path)
    bank, sender = parse_filename(filename)
    with open(file_path, "r", encoding="utf-8") as fin:
        return report_to_transactions(StringIO(fin.read()), bank, sender)
