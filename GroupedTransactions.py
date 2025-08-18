from __future__ import annotations
import csv
import io
from typing import List, Dict, Type

from Categories import Category
from ReportParsers import Transaction
import logging

logger = logging.getLogger(__name__)

class GroupedTransactions:

    CSV_HEADERS = [
        "category",
    ] + list(Transaction._fields)
    
    class _CategoryMap:
        def __init__(self):
            self._map: Dict[str, Category] = {
                cat.get_name(): cat for cat in GroupedTransactions.list_all_categories()
            }

        def get_cat(self, name: str) -> Category:
            if name not in self._map:
                raise ValueError(f"Unknown category: {name}")
            return self._map[name]

        def categories(self) -> List[Category]:
            return sorted(self._map.values(), key=lambda c: c.get_name())

        def get_names(self) -> List[str]:
            return list(sorted(self._map.keys()))

        def fill(self, existing: List[Category]) -> None:
            for cat in existing:
                self._map[cat.get_name()] = cat

    def __init__(self, *categories: Category):
        cat_map = GroupedTransactions._CategoryMap()
        cat_map.fill(categories)
        self._categories: List[Category] = cat_map.categories()

    def add_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        ungrouped = []
        for tx in transactions:
            matched = [cat for cat in self._categories if cat.is_matched(tx)]
            if len(matched) == 0:
                ungrouped.append(tx)
            elif len(matched) == 1:
                matched[0].add_transaction(tx)
            else:
                names = ', '.join(cat.get_name() for cat in matched)
                raise ValueError(f"Transaction matched multiple categories ({names}): {tx}")
        return ungrouped

    def get_categories(self) -> List[Category]:
        return self._categories
    
    def serialize(self, delimiter: str = ",") -> str:
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=delimiter)
        writer.writerow(self.CSV_HEADERS)

        row_count: int = 0
        for cat in self._categories:
            cat_name = cat.get_name()
            for tx in cat.get_transactions():
                writer.writerow([
                    cat_name,
                ] + list(tx))
                row_count+=1
        logger.info(f"serialized {row_count} grouped transactions")
        return buf.getvalue()

    @classmethod
    def deserialize(cls, csv_text: str, delimiter: str = ",") -> GroupedTransactions:
        # Empty input → empty GroupedTransactions
        if not csv_text.strip():
            return cls(*[])

        reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
        try:
            header = next(reader)
        except StopIteration:
            return cls(*[])

        if header != cls.CSV_HEADERS:
            raise ValueError(f"Unexpected CSV header. Got {header}, expected {cls.CSV_HEADERS}")

        cat_map = cls._CategoryMap()
        logger.debug(f"Map of known categories is {cat_map.get_names()}")
        
        tx_count: int = 0
        for row in reader:
            if not any(row):  # skip empty rows
                continue

            tx = Transaction.from_strings(row[1:])
            cat_map.get_cat(row[0]).add_transaction(tx)
            tx_count += 1
        logger.info(f"Deserialized {tx_count} transactions")
        filled_cats = [cat for cat in cat_map.categories() if len(cat.get_transactions()) > 0]
        logger.info(f"Found the following categories {list(c.get_name() for c in filled_cats)}")
        return cls(*cat_map.categories())

    @staticmethod
    def list_all_categories() -> List[Category]:
        out: List[Category] = []

        def rec(cls: Type[Category]):
            for sub in cls.__subclasses__():
                out.append(sub)
                rec(sub)

        rec(Category)
        concrete: List[Category] = []
        for c in out:
            try:
                concrete.append(c())
            except TypeError:
                pass
        return concrete
