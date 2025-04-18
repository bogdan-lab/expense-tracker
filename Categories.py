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


class Transport(Category):
    def __init__(self):
        super().__init__('Transport')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class HouseholdGoods(Category):
    def __init__(self):
        super().__init__('Household goods')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Restaurants(Category):
    def __init__(self):
        super().__init__('Restaurants')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Gina(Category):
    def __init__(self):
        super().__init__('Gina')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Health(Category):
    def __init__(self):
        super().__init__('Health')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Clothes(Category):
    def __init__(self):
        super().__init__('Clothes')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Child(Category):
    def __init__(self):
        super().__init__('Child')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Entertainment(Category):
    def __init__(self):
        super().__init__('Entertainment')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Taxes(Category):
    def __init__(self):
        super().__init__('Taxes')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Others(Category):
    def __init__(self):
        super().__init__('Others')

    def is_matched(self, transaction: Transaction) -> bool:
        return False
