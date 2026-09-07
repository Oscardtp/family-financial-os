from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from app.domain.value_objects.money import Money
from app.domain.value_objects.interest_rate import InterestRate, RateType
from app.financial_engine.rate_engine import RateEngine


@dataclass
class ScenarioAssumptions:
    monthly_income_change: Decimal = Decimal("0")
    monthly_expense_change: Decimal = Decimal("0")
    extra_debt_payment: Money | None = None
    new_monthly_savings: Money | None = None


@dataclass
class ProjectionResult:
    months: int
    monthly_projections: list[dict]
    debt_free_date: str | None
    projected_net_worth: Money
    projected_savings: Money


class ProjectionEngine:
    def project_scenario(
        self,
        current_monthly_income: Money,
        current_monthly_expenses: Money,
        current_debt_balance: Money,
        current_savings: Money,
        monthly_debt_payment: Money,
        months: int,
        assumptions: ScenarioAssumptions | None = None,
    ) -> ProjectionResult:
        if assumptions is None:
            assumptions = ScenarioAssumptions()

        income_factor = 1 + assumptions.monthly_income_change / Decimal("100")
        expense_factor = 1 + assumptions.monthly_expense_change / Decimal("100")

        projected_income = Money(current_monthly_income.amount * income_factor, current_monthly_income.currency)
        projected_expenses = Money(current_monthly_expenses.amount * expense_factor, current_monthly_expenses.currency)

        debt_balance = current_debt_balance
        savings = current_savings
        projections = []
        debt_free_month = None

        for month in range(1, months + 1):
            net_income = projected_income - projected_expenses

            extra = assumptions.extra_debt_payment or Money.zero()
            debt_payment = monthly_debt_payment + extra

            if debt_balance.is_positive():
                if debt_payment.amount > debt_balance.amount:
                    debt_payment = debt_balance
                debt_balance = debt_balance - debt_payment
                if debt_balance.is_negative():
                    debt_balance = Money.zero()
            else:
                debt_payment = Money.zero()

            if debt_balance.is_zero() and debt_free_month is None:
                debt_free_month = month

            savings = savings + net_income - debt_payment

            projections.append({
                "month": month,
                "income": projected_income,
                "expenses": projected_expenses,
                "net_income": net_income,
                "debt_payment": debt_payment,
                "remaining_debt": debt_balance,
                "cumulative_savings": savings,
            })

        return ProjectionResult(
            months=months,
            monthly_projections=projections,
            debt_free_date=f"Month {debt_free_month}" if debt_free_month else None,
            projected_net_worth=savings - debt_balance,
            projected_savings=savings,
        )

    def project_investment(
        self,
        current: Money,
        monthly_contribution: Money,
        annual_rate_pct: Decimal,
        months: int,
    ) -> dict:
        monthly_rate = RateEngine.to_monthly_rate(InterestRate(annual_rate_pct, RateType.EA))

        balance = current.amount
        monthly = monthly_contribution.amount
        total_contributions = current.amount
        total_interest = Decimal("0")
        breakdown = []

        for month in range(1, months + 1):
            interest = balance * monthly_rate
            balance = balance + interest + monthly
            total_contributions = total_contributions + monthly
            total_interest = total_interest + interest

            breakdown.append({
                "month": month,
                "balance": str(balance.quantize(Decimal("1"), ROUND_HALF_UP)),
                "contributions": str(total_contributions.quantize(Decimal("1"), ROUND_HALF_UP)),
                "interest": str(total_interest.quantize(Decimal("1"), ROUND_HALF_UP)),
            })

        return {
            "projected_value": str(balance.quantize(Decimal("1"), ROUND_HALF_UP)),
            "total_contributions": str(total_contributions.quantize(Decimal("1"), ROUND_HALF_UP)),
            "total_interest": str(total_interest.quantize(Decimal("1"), ROUND_HALF_UP)),
            "monthly_breakdown": breakdown,
        }
