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

def is_new_transaction(tx_list: List[Transaction], check_tx: Transaction) -> bool:
    check_key = (check_tx.sender, check_tx.receiver, check_tx.currency, check_tx.date, check_tx.amount) 
    for tx in tx_list:
        key = (tx.sender, tx.receiver, tx.currency, tx.date, tx.amount)
        if key == check_key:
            return False
    return True