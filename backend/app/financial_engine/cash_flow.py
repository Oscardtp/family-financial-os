from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from app.domain.value_objects.money import Money


@dataclass
class CashFlowResult:
    total_income: Money
    total_expenses: Money
    net_cash_flow: Money
    transactions: list[dict]
    period_start: date
    period_end: date


class CashFlowEngine:
    def calculate_cash_flow(
        self,
        transactions: list[dict],
        date_from: date,
        date_to: date,
    ) -> CashFlowResult:
        income = Money.zero()
        expenses = Money.zero()

        filtered = [
            t for t in transactions
            if date_from <= t["date"] <= date_to
        ]

        for t in filtered:
            amount = Money(Decimal(str(t["amount"])))
            if t["type"] == "income":
                income = income + amount
            elif t["type"] == "expense":
                expenses = expenses + amount

        return CashFlowResult(
            total_income=income,
            total_expenses=expenses,
            net_cash_flow=income - expenses,
            transactions=filtered,
            period_start=date_from,
            period_end=date_to,
        )

    def project_cash_flow(
        self,
        monthly_income: Money,
        monthly_expenses: Money,
        months: int,
        growth_rate: Decimal = Decimal("0.00"),
    ) -> list[dict]:
        projections = []
        current_income = monthly_income
        current_expenses = monthly_expenses

        for i in range(1, months + 1):
            net = current_income - current_expenses
            projections.append({
                "month": i,
                "income": current_income,
                "expenses": current_expenses,
                "net": net,
                "cumulative": Money(
                    sum(p["net"].amount for p in projections) + net.amount,
                    net.currency,
                ),
            })
            current_income = Money(
                current_income.amount * (1 + growth_rate / Decimal("100")),
                current_income.currency,
            )
            current_expenses = Money(
                current_expenses.amount * (1 + growth_rate / Decimal("100")),
                current_expenses.currency,
            )

        return projections
