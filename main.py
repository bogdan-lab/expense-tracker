import argparse
from ReportParsers import Transaction, parse_filename, parse_ing_transactions
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



def main():
    # print(parse_filename("Revolut_Daria_01.2025_04.2025.csv"))
    # print(parse_filename("ING_Bohdan_01.2025.csv"))
    # print(parse_filename("ABNAMRO_Bohdan_02.2025.txt"))
    # print(parse_filename("/home/bohdan/workplace/Bibliotech/Python/expense-tracker/ABNAMRO_Bohdan_02.2025.txt"))
    # print(parse_filename("Bibliotech/Python/expense-tracker/ABNAMRO_Bohdan_02.2025.txt"))
    parser = argparse.ArgumentParser(description="Process bank transaction file and group by category.")
    parser.add_argument("path", nargs='+', help="Path to the transaction file(s)")
    args = parser.parse_args()

    
    transactions = []
    for el in args.path:
        transactions += parse_ing_transactions(el)

    for el in transactions:
        print(' '.join(str(getattr(el, f)) for f in el._fields if f != 'raw'))

    # print(transactions)

    # reports = ReportAggregator(args.path)
    # transactions: list[Transaction] = (
    #     reports.get_abn_transactions() +
    #     reports.get_ing_transactions() +
    #     reports.get_revolut_transactions()
    # )

    # print(f"Number of transactions: {len(transactions)}")

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