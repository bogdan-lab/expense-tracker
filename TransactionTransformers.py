import logging
from typing import List, Set
from ReportParsers import Transaction

logger = logging.getLogger(__name__)


def lowercase_str_fields(transactions: List[Transaction]) -> List[Transaction]:
    return [
        tx._replace(
            sender=tx.sender.lower(),
            receiver=tx.receiver.lower(),
            currency=tx.currency.lower()
        )
        for tx in transactions
    ]

def drop_duplicates(transactions: List[Transaction]) -> List[Transaction]:
    seen: Set[tuple] = set()
    result: List[Transaction] = []
    for tx in transactions:
        key = (tx.sender, tx.receiver, tx.currency, tx.date, tx.amount)
        if key in seen:
            logging.warning(f"Dropped duplicate transaction: {tx}")
        else:
            seen.add(key)
            result.append(tx)
    return result