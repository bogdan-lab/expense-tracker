import argparse
from ReportParsers import Transaction
from TransactionTransformers import lowercase_str_fields, drop_duplicates
from GroupedTransactions import GroupedTransactions
from ReportAggregator import ReportAggregator
from CategoriesWriter import CsvCategoriesSaver, CsvCategoriesValidator
from ExpenseVisualizer import ExpenseVisualizer
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

GROUPED_CATEGORIES_CSV_PATH = "grouped_categories.csv"
DEFAULT_CSV_DELIMITER = "|"

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

    logger.info(f"Initial number of transactions: {len(transactions)}")

    transactions = lowercase_str_fields(transactions)
    transactions = drop_duplicates(transactions)
    
    logger.info(f"Number of transactions after duplicate dropping: {len(transactions)}")

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

    visualizer = ExpenseVisualizer(grouped.get_categories())
    visualizer.plot_combined_summary(min_percentage=2.0)


if __name__ == "__main__":
    main()