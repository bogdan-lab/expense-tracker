import matplotlib.pyplot as plt
from typing import List, Dict
from collections import defaultdict
from Categories import Category
import logging


logger = logging.getLogger(__name__)


class ExpenseVisualizer:
    def __init__(self, categories: List[Category]):
        self.categories = categories
        self.monthly_data: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        logger.info("Initializing ExpenseVisualizer and computing monthly totals...")
        self._compute_monthly_totals()

    def _compute_monthly_totals(self):
        skipped = 0
        for category in self.categories:
            name = category.get_name()
            if name == "InternalTransfers":
                skipped += 1
                continue
            txs = category.get_transactions()
            logger.debug(f"Processing {len(txs)} transactions for category: {name}")
            for tx in txs:
                month = tx.date.strftime("%Y-%m")
                self.monthly_data[name][month] += -tx.amount# Show expenses as positive bars
        logger.info(f"Skipped {skipped} category(ies) named 'InternalTransfers'")  

    def plot_monthly_expenses(self, min_percentage: float = 1.0):
        logger.info("Preparing expense data for plotting...")
        data = {cat: months for cat, months in self.monthly_data.items() if cat != "Income"}

        all_months = sorted({m for v in data.values() for m in v})
        if not all_months:
            logger.warning("No data to plot.")
            return

        last_month = all_months[-1]
        total_last_month = sum(months.get(last_month, 0.0) for months in data.values())
        threshold = (min_percentage / 100.0) * total_last_month

        filtered_data = {
            cat: months for cat, months in data.items()
            if max(months.values(), default=0.0) >= threshold
        }

        dropped = set(data) - set(filtered_data)
        if dropped:
            logger.info(f"Filtered out categories with values below {min_percentage:.2f}% of last month's total: {', '.join(sorted(dropped))}")

        categories = sorted(filtered_data.keys())
        months = sorted({m for v in filtered_data.values() for m in v})

        x = range(len(categories))
        bar_width = 0.8 / len(months)
        fig, ax = plt.subplots(figsize=(12, 6))

        for idx, month in enumerate(months):
            values = [filtered_data[cat].get(month, 0.0) for cat in categories]
            logger.debug(f"Plotting month {month} with {sum(1 for v in values if v != 0)} non-zero bars.")
            positions = [i + idx * bar_width for i in x]
            ax.bar(positions, values, width=bar_width, label=month)

        ax.set_xticks([i + bar_width * len(months) / 2 for i in x])
        ax.set_xticklabels(categories, rotation=45, ha="right")
        ax.set_ylabel("Expenses")
        ax.set_title(f"Monthly Expenses by Category (min {min_percentage:.2f}% of last month)")
        ax.legend(title="Month")

        # Annotate max monthly value for each category horizontally
        for i, cat in enumerate(categories):
            max_val = max(filtered_data[cat].values(), default=0.0)
            x_pos = i + bar_width * len(months) / 2
            ax.text(x_pos, max_val + 0.02 * max_val, f"{max_val:.0f}", ha="center", va="bottom", fontsize=8)

        plt.tight_layout()
        plt.show()
        logger.info("Expense plot displayed successfully.")