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
