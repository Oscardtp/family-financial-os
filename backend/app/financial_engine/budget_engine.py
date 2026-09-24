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


@dataclass
class BudgetProjectionItem:
    category_id: str
    category_name: str
    budgeted: Money
    spent: Money
    remaining: Money
    percentage: Decimal
    status: str
    projected_spent: Money
    projected_remaining: Money
    will_exceed: bool
    projected_overrun: Money


@dataclass
class BudgetProjectionResult:
    items: list[BudgetProjectionItem]
    total_budgeted: Money
    total_spent: Money
    total_remaining: Money
    total_projected_spent: Money
    total_projected_remaining: Money
    total_will_exceed: bool


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

    def project_budget_status(
        self,
        status: BudgetStatusResult,
        days_elapsed: int,
        days_in_month: int,
    ) -> BudgetProjectionResult:
        if days_elapsed <= 0:
            factor = Decimal("1")
        elif days_elapsed >= days_in_month:
            factor = Decimal("1")
        else:
            factor = Decimal(str(days_in_month)) / Decimal(str(days_elapsed))

        items = []
        total_projected_spent = Money.zero()
        total_will_exceed = False

        for item in status.items:
            projected_spent = item.spent * factor
            projected_remaining = item.budgeted - projected_spent
            will_exceed = projected_spent > item.budgeted
            overrun = projected_spent - item.budgeted if will_exceed else Money.zero()
            if will_exceed and not item.budgeted.is_zero():
                overrun_pct = (overrun.amount / item.budgeted.amount) * Decimal("100")
                if overrun_pct > Decimal("10"):
                    proj_status = "over"
                else:
                    proj_status = "warning"
            else:
                proj_status = item.status

            items.append(BudgetProjectionItem(
                category_id=item.category_id,
                category_name=item.category_name,
                budgeted=item.budgeted,
                spent=item.spent,
                remaining=item.remaining,
                percentage=item.percentage,
                status=proj_status,
                projected_spent=projected_spent,
                projected_remaining=projected_remaining,
                will_exceed=will_exceed,
                projected_overrun=overrun,
            ))

            total_projected_spent = total_projected_spent + projected_spent
            if will_exceed:
                total_will_exceed = True

        total_projected_remaining = status.total_budgeted - total_projected_spent

        return BudgetProjectionResult(
            items=items,
            total_budgeted=status.total_budgeted,
            total_spent=status.total_spent,
            total_remaining=status.total_remaining,
            total_projected_spent=total_projected_spent,
            total_projected_remaining=total_projected_remaining,
            total_will_exceed=total_will_exceed,
        )

    def calculate_method_distribution(
        self,
        income: Money,
        needs_pct: Decimal,
        wants_pct: Decimal,
        savings_pct: Decimal,
    ) -> dict[str, Money]:
        """FASE 6.2 — Pure function: distribute income by budget method percentages.

        Returns dict with keys: needs, wants, savings (all Money).
        No DB access, no service dependencies.
        """
        return {
            "needs": Money(income.amount * needs_pct / Decimal("100")),
            "wants": Money(income.amount * wants_pct / Decimal("100")),
            "savings": Money(income.amount * savings_pct / Decimal("100")),
        }

    def distribute_by_groups(
        self,
        income: Money,
        groups: list,
    ) -> dict[str, Money]:
        """FASE 6.3B — Pure function: distribute income across N method groups.

        groups: list of {key: str, pct: int|Decimal}. Percentages must sum to 100.
        Returns dict keyed by group key with Money values. No DB access.
        """
        total = sum(Decimal(str(g["pct"])) for g in groups)
        if total != Decimal("100"):
            raise ValueError(f"Los porcentajes deben sumar 100%. Actual: {total}%")
        return {
            g["key"]: Money(income.amount * Decimal(str(g["pct"])) / Decimal("100"))
            for g in groups
        }
