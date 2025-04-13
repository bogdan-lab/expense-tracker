from Categories import Category
from typing import List 
from ReportParsers import Transaction



class GroupedTransactions:
    def __init__(self, *categories: Category):
        self._categories: List[Category] = list(categories)

    def add_transactions(self, transactions: List[Transaction]) -> None:
        for tx in transactions:
            matched = [cat for cat in self._categories if cat.is_matched(tx)]
            if len(matched) == 0:
                raise ValueError(f"Transaction did not match any category: {tx}")
            if len(matched) > 1:
                names = ', '.join(cat.get_name() for cat in matched)
                raise ValueError(f"Transaction matched multiple categories ({names}): {tx}")
            matched[0].add_transaction(tx)

    def get_categories(self) -> List[Category]:
        return self._categories
