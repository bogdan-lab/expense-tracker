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

    # Aggregate by category and month
    monthly_totals = defaultdict(lambda: defaultdict(float))

    for category in grouped.get_categories():
        if category.get_name() == "InternalTransfers":
            continue
        for tx in category.get_transactions():
            month = tx.date.strftime("%Y-%m")
            monthly_totals[category.get_name()][month] += tx.amount

    # Identify all months across all categories
    all_months = sorted({month for m in monthly_totals.values() for month in m})

    # Build and print table header
    cell_width = 15
    header = f"| {'Category':<{cell_width}} |" + "".join(
        f" {month:>{cell_width}} |" for month in all_months)
    line = "+" + "-"*(cell_width + 2) + "+" + "+".join("-"*(cell_width + 2) for _ in all_months) + "+"

    print("\n=== Monthly Category Totals ===")
    print(line)
    print(header)
    print(line)

    # Print rows per category
    total_earn = defaultdict(float)
    total_spent = defaultdict(float)

    for category, months in monthly_totals.items():
        row = f"| {category:<{cell_width}} |"
        for month in all_months:
            amt = months.get(month, 0.0)
            row += f" {amt:>{cell_width}.2f} |"
            if amt > 0:
                total_earn[month] += amt
            else:
                total_spent[month] += amt
        print(row)
    print(line)

    # Print summary rows
    row_earn = f"| {'Total Earn':<{cell_width}} |" + "".join(
        f" {total_earn[m]:>{cell_width}.2f} |" for m in all_months)
    row_spent = f"| {'Total Spent':<{cell_width}} |" + "".join(
        f" {abs(total_spent[m]):>{cell_width}.2f} |" for m in all_months)

    print(row_earn)
    print(row_spent)
    print(line)

if __name__ == "__main__":
    main()
