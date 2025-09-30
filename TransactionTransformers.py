import logging
from typing import List, Set
from ReportParsers import Transaction

logger = logging.getLogger(__name__)

def is_new_transaction(tx_list: List[Transaction], check_tx: Transaction) -> bool:
    check_key = (check_tx.sender, check_tx.receiver, check_tx.currency, check_tx.date, check_tx.amount) 
    for tx in tx_list:
        key = (tx.sender, tx.receiver, tx.currency, tx.date, tx.amount)
        if key == check_key:
            return False
    return True