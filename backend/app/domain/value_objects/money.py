from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from app.domain.exceptions import CurrencyMismatchError, InvalidAmountError


class Money:
    """Value Object for money in COP. Always uses decimal precision."""

    def __init__(self, amount: Decimal | int | float | str, currency: str = "COP"):
        try:
            if isinstance(amount, float):
                amount = Decimal(str(amount))
            elif not isinstance(amount, Decimal):
                amount = Decimal(amount)
        except (InvalidOperation, ValueError):
            raise InvalidAmountError(str(amount))

        self.amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.currency = currency

    def _check_currency(self, other: "Money"):
        if self.currency != other.currency:
            raise CurrencyMismatchError()

    def __add__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal | int | float) -> "Money":
        if isinstance(factor, Money):
            raise TypeError("Cannot multiply Money by Money")
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __rmul__(self, factor) -> "Money":
        return self.__mul__(factor)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount >= other.amount

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

    def __str__(self) -> str:
        return f"${self.amount:,.2f} {self.currency}"

    def is_positive(self) -> bool:
        return self.amount > 0

    def is_negative(self) -> bool:
        return self.amount < 0

    def is_zero(self) -> bool:
        return self.amount == 0

    def abs(self) -> "Money":
        return Money(abs(self.amount), self.currency)

    def to_cents(self) -> int:
        return int(self.amount * 100)

    @classmethod
    def from_cents(cls, cents: int, currency: str = "COP") -> "Money":
        return cls(Decimal(cents) / Decimal(100), currency)

    @classmethod
    def zero(cls, currency: str = "COP") -> "Money":
        return cls(Decimal("0.00"), currency)
