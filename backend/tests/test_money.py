import pytest
from decimal import Decimal
from app.domain.value_objects.money import Money
from app.domain.exceptions import CurrencyMismatchError, InvalidAmountError


class TestMoneyCreation:
    def test_create_from_decimal(self):
        m = Money(Decimal("100.50"))
        assert m.amount == Decimal("100.50")
        assert m.currency == "COP"

    def test_create_from_int(self):
        m = Money(100)
        assert m.amount == Decimal("100.00")

    def test_create_from_string(self):
        m = Money("1500.75")
        assert m.amount == Decimal("1500.75")

    def test_create_from_float(self):
        m = Money(99.99)
        assert m.amount == Decimal("99.99")

    def test_custom_currency(self):
        m = Money(100, "USD")
        assert m.currency == "USD"

    def test_zero(self):
        m = Money.zero()
        assert m.amount == Decimal("0.00")
        assert m.is_zero()


class TestMoneyArithmetic:
    def test_add(self):
        a = Money("100.50")
        b = Money("200.25")
        result = a + b
        assert result.amount == Decimal("300.75")

    def test_subtract(self):
        a = Money("500")
        b = Money("200")
        result = a - b
        assert result.amount == Decimal("300.00")

    def test_multiply(self):
        m = Money("100")
        result = m * 3
        assert result.amount == Decimal("300.00")

    def test_rmul(self):
        m = Money("100")
        result = 3 * m
        assert result.amount == Decimal("300.00")

    def test_negate(self):
        m = Money("100")
        result = -m
        assert result.amount == Decimal("-100.00")

    def test_currency_mismatch_add(self):
        a = Money("100", "COP")
        b = Money("100", "USD")
        with pytest.raises(CurrencyMismatchError):
            a + b

    def test_currency_mismatch_subtract(self):
        a = Money("100", "COP")
        b = Money("100", "USD")
        with pytest.raises(CurrencyMismatchError):
            a - b


class TestMoneyComparison:
    def test_equal(self):
        assert Money("100") == Money("100")

    def test_not_equal(self):
        assert Money("100") != Money("200")

    def test_less_than(self):
        assert Money("100") < Money("200")

    def test_greater_than(self):
        assert Money("200") > Money("100")

    def test_less_equal(self):
        assert Money("100") <= Money("100")
        assert Money("100") <= Money("200")

    def test_greater_equal(self):
        assert Money("200") >= Money("100")
        assert Money("100") >= Money("100")


class TestMoneyMethods:
    def test_is_positive(self):
        assert Money("100").is_positive()
        assert not Money("-100").is_positive()
        assert not Money("0").is_positive()

    def test_is_negative(self):
        assert Money("-100").is_negative()
        assert not Money("100").is_negative()

    def test_is_zero(self):
        assert Money("0").is_zero()
        assert not Money("100").is_zero()

    def test_abs(self):
        assert Money("-100").abs() == Money("100")

    def test_to_cents(self):
        assert Money("10.50").to_cents() == 1050

    def test_from_cents(self):
        m = Money.from_cents(1050)
        assert m.amount == Decimal("10.50")

    def test_hash(self):
        assert hash(Money("100")) == hash(Money("100"))
        assert hash(Money("100")) != hash(Money("200"))

    def test_repr(self):
        assert repr(Money("100")) == "Money(100.00, 'COP')"

    def test_str(self):
        assert "$100.00 COP" in str(Money("100"))
