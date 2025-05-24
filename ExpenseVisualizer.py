import matplotlib.pyplot as plt
from typing import List, Dict
from collections import defaultdict
from Categories import Category
import logging


logger = logging.getLogger(__name__)


class ExpenseVisualizer:
    def __init__(self, categories: List[Category]):
        self.categories = categories
        self.expense_monthly_data: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.earnings_monthly_data: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        logger.info("Initializing ExpenseVisualizer and computing monthly totals...")
        self._compute_monthly_totals()

    def _compute_monthly_totals(self):
        skipped = 0
        for category in self.categories:
            name = category.get_name()
            txs = category.get_transactions()
            logger.debug(f"Processing {len(txs)} transactions for category: {name}")
            for tx in txs:
                month = tx.date.strftime("%Y-%m")
                if name == "InternalTransfers":
                    skipped += 1
                    continue
                elif name == "Income":
                    self.earnings_monthly_data[name][month] += tx.amount
                else:
                    self.expense_monthly_data[name][month] += tx.amount
        logger.info(f"Skipped {skipped} category(ies) named 'InternalTransfers'")

    def _filter_categories_by_threshold(self, min_percentage: float) -> Dict[str, Dict[str, float]]:
        data = self.expense_monthly_data
        months = sorted({m for v in data.values() for m in v})
        if not months:
            return {}

        last_month = months[-1]
        total = sum(months.get(last_month, 0.0) for months in data.values())
        threshold = (min_percentage / 100.0) * abs(total)

        filtered = {
            cat: months for cat, months in data.items()
            if abs(max(months.values(), default=0.0)) >= threshold
        }

        dropped = set(data) - set(filtered)
        if dropped:
            logger.info(f"Filtered out categories below {min_percentage:.2f}% of {last_month}: {', '.join(sorted(dropped))}")
        return filtered

    def _plot_bar_chart(self, data: Dict[str, Dict[str, float]], min_percentage: float):
        categories = sorted(data.keys())
        months = sorted({m for v in data.values() for m in v})
        x = range(len(categories))
        bar_width = 0.8 / len(months)
        fig, ax = plt.subplots(figsize=(12, 6))

        for idx, month in enumerate(months):
            values = [abs(data[cat].get(month, 0.0)) for cat in categories]
            logger.debug(f"Plotting month {month} with {sum(1 for v in values if v != 0)} bars.")
            positions = [i + idx * bar_width for i in x]
            ax.bar(positions, values, width=bar_width, label=month)

        ax.set_xticks([i + bar_width * len(months) / 2 for i in x])
        ax.set_xticklabels(categories, rotation=45, ha="right")
        ax.set_ylabel("Expenses")
        ax.set_title(f"Monthly Expenses by Category (min {min_percentage:.2f}% of last month)")
        ax.legend(title="Month")

        for i, cat in enumerate(categories):
            max_val = max(abs(v) for v in data[cat].values())
            x_pos = i + bar_width * len(months) / 2
            ax.text(x_pos, max_val + 0.02 * max_val, f"{max_val:.0f}", ha="center", va="bottom", fontsize=8)

        plt.tight_layout()
        plt.show()

    def plot_monthly_expenses(self, min_percentage: float = 1.0):
        logger.info("Preparing data for expense plot...")
        filtered_data = self._filter_categories_by_threshold(min_percentage)
        if not filtered_data:
            logger.warning("No categories meet threshold. Skipping plot.")
            return
        self._plot_bar_chart(filtered_data, min_percentage)

    def plot_monthly_totals(self):
        logger.info("Computing monthly totals for expenses and earnings from split data...")
        total_expenses: Dict[str, float] = defaultdict(float)
        total_earnings: Dict[str, float] = defaultdict(float)

        for cat, months in self.expense_monthly_data.items():
            for month, amount in months.items():
                total_expenses[month] += amount

        for cat, months in self.earnings_monthly_data.items():
            for month, amount in months.items():
                total_earnings[month] += amount

        months = sorted(set(total_expenses) | set(total_earnings))
        x = range(len(months))
        bar_width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))

        exp_values = [abs(total_expenses.get(m, 0.0)) for m in months]
        earn_values = [abs(total_earnings.get(m, 0.0)) for m in months]

        exp_bars = ax.bar([i - bar_width / 2 for i in x], exp_values, width=bar_width, label="Expenses")
        earn_bars = ax.bar([i + bar_width / 2 for i in x], earn_values, width=bar_width, label="Earnings")

        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45, ha="right")
        ax.set_ylabel("Amount")
        ax.set_title("Total Monthly Expenses vs. Earnings")
        ax.legend()

        for bar in exp_bars + earn_bars:
            height = bar.get_height()
            ax.annotate(f"{height:.0f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.show()
