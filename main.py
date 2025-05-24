import argparse
from ReportParsers import Transaction
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
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)



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

    print(f"Number of transactions: {len(transactions)}")

    grouped = GroupedTransactions(Groceries(), Transport(), 
                                  HouseholdGoods(), Restaurants(), 
                                  Gina(), Health(), Clothes(), 
                                  Child(), Entertainment(), Taxes(),
                                  VVE(), Bills(), Insurance(), Banks(),
                                  InternalTransfers(), Services(), Apartment(), 
                                  Income(), Documents(), Others())
    ungrouped = grouped.add_transactions(transactions)



    assert len(ungrouped) == 0

    visualizer = ExpenseVisualizer(grouped.get_categories())

    # visualizer.plot_monthly_expenses(min_percentage=2)
    visualizer.plot_monthly_totals()




if __name__ == "__main__":
    main()