from dataclasses import dataclass
from decimal import Decimal
from app.domain.value_objects.money import Money
from app.financial_engine.money_operations import MoneyOperations


@dataclass
class BudgetStatusItem:
    category_id: str
    category_name: str
    budgeted: Money
    spent: Money
    remaining: Money
    percentage: Decimal
    status: str  # ok, warning, exceeded


@dataclass
class BudgetStatusResult:
    items: list[BudgetStatusItem]
    total_budgeted: Money
    total_spent: Money
    total_remaining: Money


class BudgetEngine:
    def calculate_budget_status(
        self,
        budgets: list[dict],
        spending_by_category: list[dict],
    ) -> BudgetStatusResult:
        items = []
        total_budgeted = Money.zero()
        total_spent = Money.zero()

        budget_map = {str(b["category_id"]): b for b in budgets}

        for spending in spending_by_category:
            cat_id = str(spending["category_id"])
            budgeted = Money(Decimal(str(budget_map.get(cat_id, {}).get("amount", 0))))
            spent = Money(Decimal(str(spending["total"])))
            remaining = budgeted - spent
            percentage = MoneyOperations.percentage(spent, budgeted) if not budgeted.is_zero() else Decimal("0")

            if percentage <= Decimal("80"):
                status = "ok"
            elif percentage <= Decimal("100"):
                status = "warning"
            else:
                status = "exceeded"

            items.append(BudgetStatusItem(
                category_id=cat_id,
                category_name=spending.get("category_name", ""),
                budgeted=budgeted,
                spent=spent,
                remaining=remaining,
                percentage=percentage,
                status=status,
            ))

            total_budgeted = total_budgeted + budgeted
            total_spent = total_spent + spent

        return BudgetStatusResult(
            items=items,
            total_budgeted=total_budgeted,
            total_spent=total_spent,
            total_remaining=total_budgeted - total_spent,
        )

    def detect_overruns(self, status: BudgetStatusResult) -> list[BudgetStatusItem]:
        return [item for item in status.items if item.status == "exceeded"]
