from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from app.domain.value_objects.money import Money
from app.domain.value_objects.interest_rate import InterestRate, RateType
from app.financial_engine.money_operations import MoneyOperations
from app.financial_engine.rate_engine import RateEngine
from app.financial_engine.helpers import months_between


@dataclass
class SavingsGoalProgress:
    id: str
    name: str
    target: Money
    current: Money
    percentage: Decimal
    remaining: Money
    on_track: bool
    months_to_goal: int | None


@dataclass
class SavingsProgressResult:
    goals: list[SavingsGoalProgress]
    total_target: Money
    total_current: Money
    overall_percentage: Decimal
    savings_rate: Decimal | None


class SavingsEngine:
    def calculate_progress(
        self,
        goals: list[dict],
        monthly_income: Money | None = None,
        monthly_expenses: Money | None = None,
    ) -> SavingsProgressResult:
        progress_goals = []
        total_target = Money.zero()
        total_current = Money.zero()

        today = date.today()

        for goal in goals:
            target = Money(Decimal(str(goal["target_amount"])))
            current = Money(Decimal(str(goal["current_amount"])))
            remaining = target - current
            percentage = MoneyOperations.percentage(current, target) if not target.is_zero() else Decimal("0")

            months_to_goal = None
            if goal.get("target_date") and remaining.is_positive():
                target_date = goal["target_date"]
                if isinstance(target_date, str):
                    target_date = date.fromisoformat(target_date)
                months_left = months_between(today, target_date)
                if months_left > 0:
                    monthly_needed = Money(remaining.amount / Decimal(str(months_left)), remaining.currency)
                    months_to_goal = months_left

            on_track = percentage >= Decimal("100") or (
                months_to_goal is not None and months_to_goal > 0
            )

            progress_goals.append(SavingsGoalProgress(
                id=str(goal["id"]),
                name=goal["name"],
                target=target,
                current=current,
                percentage=percentage,
                remaining=remaining,
                on_track=on_track,
                months_to_goal=months_to_goal,
            ))

            total_target = total_target + target
            total_current = total_current + current

        overall = MoneyOperations.percentage(total_current, total_target) if not total_target.is_zero() else Decimal("0")

        savings_rate = None
        if monthly_income and monthly_expenses and monthly_income.is_positive():
            savings_amount = monthly_income - monthly_expenses
            savings_rate = MoneyOperations.percentage(savings_amount, monthly_income)

        return SavingsProgressResult(
            goals=progress_goals,
            total_target=total_target,
            total_current=total_current,
            overall_percentage=overall,
            savings_rate=savings_rate,
        )

    def calculate_goal_projection(
        self,
        current_amount: Decimal,
        monthly_contribution: Decimal,
        target_amount: Decimal,
        expected_return_rate: Decimal | None = None,
        horizon_months: int | None = None,
    ) -> dict:
        current = Decimal(str(current_amount))
        monthly = Decimal(str(monthly_contribution))
        target = Decimal(str(target_amount))

        if expected_return_rate is not None:
            monthly_rate = RateEngine.to_monthly_rate(InterestRate(Decimal(str(expected_return_rate)), RateType.EA))
        else:
            monthly_rate = Decimal("0")

        months_to_goal = None
        breakdown = []
        balance = current
        total_contributions = current
        total_interest = Decimal("0")

        max_months = horizon_months or 360

        for month in range(1, max_months + 1):
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

            if months_to_goal is None and balance >= target:
                months_to_goal = month

        return {
            "months_to_goal": months_to_goal,
            "projected_value": str(balance.quantize(Decimal("1"), ROUND_HALF_UP)),
            "total_contributions": str(total_contributions.quantize(Decimal("1"), ROUND_HALF_UP)),
            "total_interest": str(total_interest.quantize(Decimal("1"), ROUND_HALF_UP)),
            "monthly_breakdown": breakdown[:36],
        }
