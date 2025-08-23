import os
import logging
import shutil
from abc import ABC, abstractmethod
from GroupedTransactions import GroupedTransactions

logger = logging.getLogger(__name__)

class CategoriesSaver(ABC):
    @abstractmethod
    def save(self, grouped: GroupedTransactions, path: str) -> None:
        pass


class CsvCategoriesSaver(CategoriesSaver):
    def save(self, grouped: GroupedTransactions, path: str, delimiter: str) -> None:
        if os.path.exists(path):
            backup_path = path + ".backup"
            shutil.copy2(path, backup_path)
            logger.warning(f"Existing file backed up to {backup_path}")

        csv_text = grouped.serialize(delimiter=delimiter)
        with open(path, mode="w", encoding="utf-8") as f:
            f.write(csv_text)
        logger.info(f"Wrote grouped transactions to {path}")


class CsvCategoriesValidator(CategoriesSaver):
    def save(self, grouped: GroupedTransactions, path: str, delimiter: str) -> None:
        if not os.path.exists(path):
            raise ValueError(f"File {path} does not exist. Cannot validate!")

        with open(path, mode="r", encoding="utf-8") as f:
            stored_text = f.read()

        loaded = GroupedTransactions.deserialize(stored_text, delimiter=delimiter)
        expected = grouped.get_categories()
        actual = loaded.get_categories()

        if len(actual) != len(expected):
            raise ValueError(f"Mismatch of category number actual: {len(actual)}; expected: {len(expected)}")
        for e_cat, a_cat in zip(expected, actual):
            if e_cat.get_name() != a_cat.get_name():
                raise ValueError(f"Category mismatch: expected '{e_cat.get_name()}', got '{a_cat.get_name()}'")
            e_tx = e_cat.get_transactions()
            a_tx = a_cat.get_transactions()
            if e_tx != a_tx:
                raise ValueError(f"Transaction mismatch in category '{e_cat.get_name()}'")

        logger.info(f"Validation passed: contents in {path} match current grouped transactions")
