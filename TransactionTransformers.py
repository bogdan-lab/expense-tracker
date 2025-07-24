import logging
from typing import List
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

