import argparse
from ReportParsers import Transaction, Bank, report_to_transactions, parse_filename
from GroupedTransactions import load_grouped_transactions_from_dbase, GroupedTransactions, compare_categories
from Categories import Ungrouped
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

    grouped = load_grouped_transactions_from_dbase(db_path, db_delimiter)
    logger.info(f"Transaction groups after load:\n{grouped.format_category_counts()}")

    grouped.add_transactions(transactions)
    logger.info(f"Transaction groups after update:\n{grouped.format_category_counts()}")
    
    CsvCategoriesSaver().save(grouped=grouped, path=db_path, delimiter=db_delimiter)


def update_database_from_file(db_path: str, db_delimiter: str, file_path: str) -> None:
    assert os.path.isfile(file_path)
    filename = os.path.basename(file_path)
    bank, sender = parse_filename(filename)
    with open(file_path, 'r', encoding="utf-8") as fin:
        update_database(db_path, db_delimiter, StringIO(fin.read()), bank, sender)


def plot_current_db_statistics(db_path: str, db_delimiter: str) -> Figure:
    return plot_statistics(load_grouped_transactions_from_dbase(db_path, db_delimiter))


def validate_database_stays_the_same(db_path: str, db_delimiter: str) -> None:
    current = load_grouped_transactions_from_dbase(db_path, db_delimiter)
    logger.info(f"Transaction groups after load:\n{current.format_category_counts()}")
    current.get_category(Ungrouped).clear()
    logger.info(f"Dropping ungrouped transactions:\n{current.format_category_counts()}")
    
    all_trs = []
    for c in current.get_categories():
        all_trs += c.get_transactions()
    
    new_grouped = GroupedTransactions()
    new_grouped.add_transactions(all_trs)
    logger.info(f"Transaction groups after rematching:\n{new_grouped.format_category_counts()}")
        
    error_msg = compare_categories(actual=new_grouped, expected=current)
    if error_msg is not None:
        raise RuntimeError(error_msg)


def process_ungrouped_transactions(db_path: str, db_delimiter: str) -> None:
    current = load_grouped_transactions_from_dbase(db_path, db_delimiter)
    logger.info(f"Transaction groups after load:\n{current.format_category_counts()}")
    
    ungrouped_trs = current.get_category(Ungrouped).get_transactions()
    logger.info(f"Number of ungrouped transactions {len(ungrouped_trs)}")
    current.get_category(Ungrouped).clear()
    
    current.add_transactions(ungrouped_trs)
    logger.info(f"Number of ungrouped transactions {len(current.get_category(Ungrouped).get_transactions())}")
    
    CsvCategoriesSaver().save(grouped=current, path=db_path, delimiter=db_delimiter)


def main():
    parser = argparse.ArgumentParser(description="Process bank transaction file and group by category.")
    mx = parser.add_mutually_exclusive_group()
    mx.add_argument("--validate-db", action="store_true", help="Validate DB stays the same after rematching.")
    mx.add_argument("--process-ungrouped", action="store_true", help="Try to rematch currently ungrouped transactions.")
    mx.add_argument("--show-stats", action="store_true", help="Show current statistics without updating the DB.")
    parser.add_argument("--path", type=str, help="Path to the transaction file(s)", required=False)
    args = parser.parse_args()

    if args.validate_db:
        validate_database_stays_the_same(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER)
        return

    if args.process_ungrouped:
        process_ungrouped_transactions(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER)
        return

    if args.show_stats:
        plot_current_db_statistics(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER)
        plt.show()
        return

    if not args.path:
        parser.error("update mode requires at least one path (file or directory)")

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