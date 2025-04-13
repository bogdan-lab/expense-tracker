from abc import ABC, abstractmethod
from typing import List
from ReportParsers import Transaction


class Category(ABC):
    def __init__(self, name: str):
        self._name = name
        self._transactions: List[Transaction] = []
        self._total: float = 0.0

    def get_name(self) -> str:
        return self._name

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)
        self._total += transaction.amount

    def get_total(self) -> float:
        return self._total

    def get_transactions(self) -> List[Transaction]:
        return self._transactions

    @abstractmethod
    def is_matched(self, transaction: Transaction) -> bool:
        pass


class Groceries(Category):
    def __init__(self):
        super().__init__('Groceries')

    def is_matched(self, transaction: Transaction) -> bool:
        return 'albert heijn' in transaction.description.lower()


class NotGroceries(Category):
    def __init__(self):
        super().__init__('NotGroceries')

    def is_matched(self, transaction: Transaction) -> bool:
        return 'albert heijn' not in transaction.description.lower()


