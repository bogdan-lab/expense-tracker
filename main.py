import argparse
from ReportParsers import Transaction, Bank, report_to_transactions, parse_filename
from GroupedTransactions import load_grouped_transactions_from_dbase
from CategoriesWriter import CsvCategoriesSaver
from ExpenseVisualizer import plot_statistics
import logging
import matplotlib.pyplot as plt
from Constants import DEFAULT_CSV_DELIMITER, GROUPED_CATEGORIES_CSV_PATH
from io import StringIO
import os
from matplotlib.figure import Figure


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def update_database(db_path: str, db_delimiter: str, report: StringIO, bank: Bank, sender: str) -> None:
    transactions: list[Transaction] = report_to_transactions(report, bank, sender)

    logger.info(f"Number of transactions in update: {len(transactions)}")

    transaction_str = lambda g: "\n".join(f"{c.get_name()}:\t{len(c.get_transactions())}" for c in g.get_categories())

    grouped = load_grouped_transactions_from_dbase(db_path, db_delimiter)
    logger.info(f"Transaction groups after load:\n {transaction_str(grouped)}")

    grouped.add_transactions(transactions)
    logger.info(f"Transaction groups after update:\n {transaction_str(grouped)}")
    
    CsvCategoriesSaver().save(grouped=grouped, path=db_path, delimiter=db_delimiter)


def update_database_from_file(db_path: str, db_delimiter: str, file_path: str) -> None:
    assert os.path.isfile(file_path)
    filename = os.path.basename(file_path)
    bank, sender = parse_filename(filename)
    with open(file_path, 'r', encoding="utf-8") as fin:
        update_database(db_path, db_delimiter, StringIO(fin.read()), bank, sender)


def plot_current_db_statistics(db_path: str, db_delimiter: str) -> Figure:
    return plot_statistics(load_grouped_transactions_from_dbase(db_path, db_delimiter))

def validate_database_stays_the_same():
    # TODO
    # CsvCategoriesValidator().save(grouped=grouped, path=GROUPED_CATEGORIES_CSV_PATH, delimiter=DEFAULT_CSV_DELIMITER)
    pass

def process_ungrouped_transactions():
    # TODO
    pass

def main():
    parser = argparse.ArgumentParser(description="Process bank transaction file and group by category.")
    parser.add_argument("path", type=str, help="Path to the transaction file(s)")
    args = parser.parse_args()

    file_paths = []
    if os.path.isfile(args.path):
        file_paths.append(args.path)
    else:
        for entry in os.listdir(args.path):
            full_path = os.path.join(args.path, entry)
            if os.path.isfile(full_path):
                file_paths.append(full_path)

    for fp in file_paths:
        update_database_from_file(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER, fp)
                
    plot_current_db_statistics(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER)
    plt.show()


if __name__ == "__main__":
    main()