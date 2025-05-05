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

    grouped = GroupedTransactions(Groceries(), Transport(), 
                                  HouseholdGoods(), Restaurants(), 
                                  Gina(), Health(), Clothes(), 
                                  Child(), Entertainment(), Taxes(),
                                  VVE(), Bills(), Insurance(), Banks(),
                                  InternalTransfers(), Services(), Apartment(), 
                                  Income(), Documents(), Others())
    ungrouped = grouped.add_transactions(transactions)

    print("\n==================== GROUPED TRANSACTIONS ====================\n")
    for category in grouped.get_categories():
        txs = category.get_transactions()
        print(f"{'=' * 10} CATEGORY: {category.get_name().upper()} ({len(txs)} transactions) {'=' * 10}\n")
        for tx in txs:
            print(f"  - {tx.description}")
        print("\n--------------------------------------------------------------\n")

    if ungrouped:
        print(f"==================== UNGROUPED TRANSACTIONS ({len(ungrouped)}) ===================\n")
        for tx in ungrouped:
            print(f"  - {tx.date}\t{tx.amount}\t{tx.description}")
        print("\n==============================================================\n")

    total_earn = 0.0
    total_spent = 0.0
    earn_categories = []
    spent_categories = []

    print("\n=== Category Totals ===")
    print(f"{'Category':<20} {'Amount':>12}")
    print("-" * 32)
    for category in grouped.get_categories():
        if category.get_name() == "InternalTransfers":
            continue
        category_total = category.get_total()
        print(f"{category.get_name():<20} {category_total:12.2f}")
        if category_total > 0:
            total_earn += category_total
            earn_categories.append(category.get_name())
        else:
            total_spent += category_total
            spent_categories.append(category.get_name())

    print("\n=== Summary ===")
    print(f"Total Earn : {total_earn:.2f} from {', '.join(earn_categories)}")
    print(f"Total Spent: {abs(total_spent):.2f} from {', '.join(spent_categories)}")
    


if __name__ == "__main__":
    main()
