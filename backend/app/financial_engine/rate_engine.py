from decimal import Decimal
from app.domain.value_objects.interest_rate import InterestRate, RateType


class RateEngine:
    @staticmethod
    def to_monthly_rate(rate: InterestRate) -> Decimal:
        v = rate.value / Decimal("100")
        if rate.rate_type == RateType.EA:
            return (Decimal("1") + v) ** (Decimal("1") / Decimal("12")) - Decimal("1")
        if rate.rate_type == RateType.EM:
            return v
        if rate.rate_type == RateType.NOMINAL:
            return v / Decimal("12")
        if rate.rate_type == RateType.DAILY:
            return (Decimal("1") + v) ** Decimal("30") - Decimal("1")
        return (Decimal("1") + v) ** (Decimal("1") / Decimal("12")) - Decimal("1")
