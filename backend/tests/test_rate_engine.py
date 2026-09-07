import pytest
from decimal import Decimal
from app.domain.value_objects.interest_rate import InterestRate, RateType
from app.financial_engine.rate_engine import RateEngine


class TestRateEngine:
    def test_ea_24_percent(self):
        rate = InterestRate(Decimal("24"), RateType.EA)
        monthly = RateEngine.to_monthly_rate(rate)
        expected = (Decimal("1") + Decimal("0.24")) ** (Decimal("1") / Decimal("12")) - Decimal("1")
        assert monthly == expected

    def test_em_direct(self):
        rate = InterestRate(Decimal("2"), RateType.EM)
        monthly = RateEngine.to_monthly_rate(rate)
        assert monthly == Decimal("0.02")

    def test_nominal_annual(self):
        rate = InterestRate(Decimal("24"), RateType.NOMINAL)
        monthly = RateEngine.to_monthly_rate(rate)
        assert monthly == Decimal("0.02")

    def test_daily_rate(self):
        rate = InterestRate(Decimal("0.1"), RateType.DAILY)
        monthly = RateEngine.to_monthly_rate(rate)
        expected = (Decimal("1") + Decimal("0.001")) ** Decimal("30") - Decimal("1")
        assert monthly == expected

    def test_zero_rate_ea(self):
        rate = InterestRate(Decimal("0"), RateType.EA)
        monthly = RateEngine.to_monthly_rate(rate)
        assert monthly == Decimal("0")

    def test_zero_rate_nominal(self):
        rate = InterestRate(Decimal("0"), RateType.NOMINAL)
        monthly = RateEngine.to_monthly_rate(rate)
        assert monthly == Decimal("0")

    def test_default_is_ea(self):
        rate = InterestRate(Decimal("12"))
        assert rate.rate_type == RateType.EA
        monthly = RateEngine.to_monthly_rate(rate)
        expected = (Decimal("1") + Decimal("0.12")) ** (Decimal("1") / Decimal("12")) - Decimal("1")
        assert monthly == expected

    def test_fallback_unknown_type(self):
        rate = InterestRate(Decimal("12"), "UNKNOWN")
        monthly = RateEngine.to_monthly_rate(rate)
        expected = (Decimal("1") + Decimal("0.12")) ** (Decimal("1") / Decimal("12")) - Decimal("1")
        assert monthly == expected
