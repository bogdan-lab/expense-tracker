from abc import ABC, abstractmethod
from typing import List
from ReportParsers import Transaction
import re


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
        patterns = [
            re.compile(r"Albert Heijn", re.IGNORECASE),
            re.compile(r"AH to Go", re.IGNORECASE),
            re.compile(r"Kiosk"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Transport(Category):
    def __init__(self):
        super().__init__('Transport')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r".*NS.*REIZIGERS.*", re.IGNORECASE),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Insurance(Category):
    def __init__(self):
        super().__init__('Insurance')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"ABN AMRO SCHADEV NV"),
            re.compile(r"Premie Zilveren Kruis Relatienummer 190009575"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class HouseholdGoods(Category):
    def __init__(self):
        super().__init__('Household goods')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"(?i)(\bGamma\b|/GAMMA/)"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Restaurants(Category):
    def __init__(self):
        super().__init__('Restaurants')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"McTurfmarkt.*NR:6NXV02", re.IGNORECASE),  # MacDonalds on Turfmarkt street
            re.compile(r"BK Den Haag Spui"), # BK for Burger King
            re.compile(r"Starbucks"),
            re.compile(r"Cafe Van Beek"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Gina(Category):
    def __init__(self):
        super().__init__('Gina')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Health(Category):
    def __init__(self):
        super().__init__('Health')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Holland & Barrett")
        ]
        return any(p.search(transaction.description) for p in patterns)




class Clothes(Category):
    def __init__(self):
        super().__init__('Clothes')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Child(Category):
    def __init__(self):
        super().__init__('Child')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Baby-Dump B.V.", re.IGNORECASE)
        ]
        return any(p.search(transaction.description) for p in patterns)


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

class VVE(Category):
    def __init__(self):
        super().__init__('VVE')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"VvE La Fenetre", re.IGNORECASE)
        ]
        return any(p.search(transaction.description) for p in patterns)


class Bills(Category):
    def __init__(self):
        super().__init__('Bills')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"/NAME/ENECO\b"),
            re.compile(r"/NAME/ZIGGO SERVICES BV/"),
            re.compile(r"Naam: ODIDO NETHERLANDS B.V."),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Banks(Category):
    def __init__(self):
        super().__init__('Banks')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"ABN AMRO Bank N.V."),
        ]
        return any(p.search(transaction.description) for p in patterns)

class InternalTransfers(Category):
    def __init__(self):
        super().__init__('InternalTransfers')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Naam: D. Krymova"),
            re.compile(r"Naam: B LAKATOSH"),
            re.compile(r"Hr B Lakatosh,Mw D Krymova"),
            re.compile(r"/TRTP/iDEAL/IBAN/NL58CITI2032329913/BIC/CITINL2X/NAME/Revolut Bank UAB"),
            re.compile(r"NAME/Interactive Brokers Ireland Limited"),
            re.compile(r"NAME/A LAKATOSH"),
        ]
        return any(p.search(transaction.description) for p in patterns)



class Others(Category):
    def __init__(self):
        super().__init__('Others')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"CCV\*Kroonenberg Groep"),
            re.compile(r"NAME/Greenwheels\b"),
            re.compile(r"\bDen Haag\b.*\bNR:55800440"),

        ]
        return any(p.search(transaction.description) for p in patterns)


