import os
from typing import List, Dict
from ReportParsers import (
    parse_abn_amro_transactions,
    parse_ing_transactions,
    parse_revolut_transactions,
    Transaction
)


class ReportAggregator:
    def __init__(self, path: str):
        self.files_by_bank: Dict[str, List[str]] = {"ABN": [], "ING": [], "Revolut": []}
        self._collect_files(path)

    def _collect_files(self, path: str):
        if os.path.isfile(path):
            self._process_file(os.path.basename(path), path)
        else:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isfile(full_path):
                    self._process_file(entry, full_path)

    def _process_file(self, filename: str, full_path: str):
        if "_" not in filename:
            print(f"Ignoring file without bank prefix: {filename}")
            return
        bank = filename.split('_')[0]
        if bank == "ABNAMRO":
            self.files_by_bank["ABN"].append(full_path)
        elif bank == "ING":
            self.files_by_bank["ING"].append(full_path)
        elif bank == "Revolut":
            self.files_by_bank["Revolut"].append(full_path)
        else:
            print(f"Ignoring file with unknown bank prefix '{bank}': {filename}")

    def get_abn_transactions(self) -> List[Transaction]:
        return [tx for f in self.files_by_bank["ABN"] for tx in parse_abn_amro_transactions(f)]

    def get_ing_transactions(self) -> List[Transaction]:
        return [tx for f in self.files_by_bank["ING"] for tx in parse_ing_transactions(f)]

    def get_revolut_transactions(self) -> List[Transaction]:
        return [tx for f in self.files_by_bank["Revolut"] for tx in parse_revolut_transactions(f)]
