import argparse
from ReportParsers import parse_abn_amro_transactions
from Categories import (
    Groceries, Transport, HouseholdGoods, Restaurants, 
    Gina, Health, Clothes, Child, Entertainment, Taxes, 
    VVE, Bills, Insurance, Banks, InternalTransfers, Others
)
from GroupedTransactions import GroupedTransactions

def main():
    parser = argparse.ArgumentParser(description="Process bank transaction file and group by category.")
    parser.add_argument("file_path", type=str, help="Path to the transaction file")
    args = parser.parse_args()

    transactions = parse_abn_amro_transactions(args.file_path)
    grouped = GroupedTransactions(Groceries(), Transport(), 
                                  HouseholdGoods(), Restaurants(), 
                                  Gina(), Health(), Clothes(), 
                                  Child(), Entertainment(), Taxes(),
                                  VVE(), Bills(), Insurance(), Banks(),
                                  InternalTransfers(), Others())
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

if __name__ == "__main__":
    main()
