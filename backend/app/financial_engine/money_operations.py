from decimal import Decimal, ROUND_HALF_UP
from app.domain.value_objects.money import Money
from app.domain.value_objects.interest_rate import InterestRate, RateType
from app.financial_engine.rate_engine import RateEngine


class MoneyOperations:
    """Static operations for Money calculations. Deterministic and verifiable."""

    @staticmethod
    def sum_amounts(amounts: list[Money]) -> Money:
        if not amounts:
            return Money.zero()
        result = Money.zero(amounts[0].currency)
        for amount in amounts:
            result = result + amount
        return result

    @staticmethod
    def average(amounts: list[Money]) -> Money:
        if not amounts:
            return Money.zero()
        total = MoneyOperations.sum_amounts(amounts)
        count = Decimal(str(len(amounts)))
        return Money(total.amount / count, total.currency)

    @staticmethod
    def percentage(part: Money, whole: Money) -> Decimal:
        if whole.is_zero():
            return Decimal("0.00")
        return (part.amount / whole.amount * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @staticmethod
    def apply_interest(principal: Money, rate: Decimal, periods: int = 1, rate_type: str = "EA") -> Money:
        try:
            rt = RateType(rate_type)
        except ValueError:
            rt = RateType.EA
        monthly_rate = RateEngine.to_monthly_rate(InterestRate(rate, rt))
        factor = (Decimal("1") + monthly_rate) ** periods
        return Money(principal.amount * factor, principal.currency)

    @staticmethod
    def amortize_payment(
        balance: Money, rate: Decimal, total_periods: int, current_period: int = 1, rate_type: str = "EA"
    ) -> dict:
        try:
            rt = RateType(rate_type)
        except ValueError:
            rt = RateType.EA
        monthly_rate = RateEngine.to_monthly_rate(InterestRate(rate, rt))
        if monthly_rate == 0:
            payment = balance.amount / Decimal(str(total_periods))
            return {
                "payment": Money(payment, balance.currency),
                "principal": Money(payment, balance.currency),
                "interest": Money.zero(balance.currency),
                "remaining": Money(
                    balance.amount - payment,
                    balance.currency,
                ),
            }

        factor = (1 + monthly_rate) ** Decimal(str(total_periods))
        payment = (balance.amount * monthly_rate * factor) / (factor - 1)
        interest = balance.amount * monthly_rate
        principal = payment - interest

        return {
            "payment": Money(payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), balance.currency),
            "principal": Money(principal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), balance.currency),
            "interest": Money(interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), balance.currency),
            "remaining": Money(
                (balance.amount - principal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                balance.currency,
            ),
        }
