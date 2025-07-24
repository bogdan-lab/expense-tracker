import argparse
from ReportParsers import Transaction
from TransactionTransformers import lowercase_str_fields, drop_duplicates
from Categories import (
    Groceries, Transport, HouseholdGoods, Restaurants, 
    Gina, Health, Clothes, Child, Entertainment, Taxes, 
    VVE, Bills, Insurance, Banks, InternalTransfers,
    Services, Apartment, Income, Documents, Others
)
from GroupedTransactions import GroupedTransactions
from ReportAggregator import ReportAggregator
from collections import defaultdict
from ExpenseVisualizer import ExpenseVisualizer
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Process bank transaction file and group by category.")
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

    # for tx in transactions:
    #     logger.info(' '.join(str(getattr(tx, f)) for f in tx._fields if f != 'raw'))

    # grouped = GroupedTransactions(Groceries(), Transport(), 
    #                               HouseholdGoods(), Restaurants(), 
    #                               Gina(), Health(), Clothes(), 
    #                               Child(), Entertainment(), Taxes(),
    #                               VVE(), Bills(), Insurance(), Banks(),
    #                               InternalTransfers(), Services(), Apartment(), 
    #                               Income(), Documents(), Others())
    # ungrouped = grouped.add_transactions(transactions)



    # assert len(ungrouped) == 0

    # visualizer = ExpenseVisualizer(grouped.get_categories())

    # visualizer.plot_combined_summary(min_percentage=2.0)




if __name__ == "__main__":
    main()