import argparse
from ReportParsers import Transaction, Bank, report_to_transactions
from TransactionTransformers import drop_duplicates
from GroupedTransactions import GroupedTransactions, load_grouped_transactions_from_dbase
from ReportAggregator import ReportAggregator
from CategoriesWriter import CsvCategoriesSaver, CsvCategoriesValidator
from ExpenseVisualizer import plot_statistics
import logging
import matplotlib.pyplot as plt
from Constants import DEFAULT_CSV_DELIMITER, GROUPED_CATEGORIES_CSV_PATH
from io import StringIO


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def update_database(db_path: str, db_delimiter: str, report: StringIO, bank: Bank, sender: str) -> None:
    transactions: list[Transaction] = report_to_transactions(report, bank, sender)

    logger.info(f"Number of transactions: {len(transactions)}")

    grouped = load_grouped_transactions_from_dbase(db_path, db_delimiter)

    ungrouped = grouped.add_transactions(transactions)

    ungrouped_str = '\n'.join(('\t'.join((t.sender, t.receiver, str(t.date), str(t.amount))) for t in ungrouped))
    logger.info(f"Number of ungrouped transactions: {len(ungrouped)}")
    if len(ungrouped) > 0:
        logger.error(f"List of ungrouped transactions: {ungrouped_str}")

    CsvCategoriesSaver().save(grouped=grouped, path=db_path, delimiter=db_delimiter)


def main():
    parser = argparse.ArgumentParser(description="Process bank transaction file and group by category.")
    parser.add_argument(
    "--update_csv",
    action="store_true",
    default=False,
    help="Overwrite current csv storage with newly generated data (default: False)")
    parser.add_argument("path", type=str, help="Path to the transaction file(s)")
    args = parser.parse_args()

    reports = ReportAggregator(args.path)
    transactions: list[Transaction] = (
        reports.get_abn_transactions() +
        reports.get_ing_transactions() +
        reports.get_revolut_transactions()
    )

    logger.info(f"Number of transactions: {len(transactions)}")

    grouped = GroupedTransactions()
    ungrouped = grouped.add_transactions(transactions)

    ungrouped_str = '\n'.join(('\t'.join((t.sender, t.receiver, str(t.date), str(t.amount))) for t in ungrouped))
    logger.info(f"Number of ungrouped transactions: {len(ungrouped)}")
    if len(ungrouped) > 0:
        logger.error(f"List of ungrouped transactions: {ungrouped_str}")

    if args.update_csv:
        CsvCategoriesSaver().save(grouped=grouped, path=GROUPED_CATEGORIES_CSV_PATH, delimiter=DEFAULT_CSV_DELIMITER)
    else:
        CsvCategoriesValidator().save(grouped=grouped, path=GROUPED_CATEGORIES_CSV_PATH, delimiter=DEFAULT_CSV_DELIMITER)

    plot_statistics(grouped)
    plt.show()


if __name__ == "__main__":
    main()