"""Financial Engine - Pure computation, no I/O."""

from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import List, Optional
import uuid


# ── Money ──────────────────────────────────────────────
class Money:
    """Representa una cantidad monetaria como entero en la unidad menor (centavos)."""

    __slots__ = ("_value", "_currency", "_scale")

    def __init__(self, value: int, currency: str, scale: int = 2):
        if value < 0:
            raise ValueError("Cannot represent negative money")
        self._value = int(value)
        self._currency = currency
        self._scale = scale

    @property
    def value(self) -> int:
        return self._value

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def scale(self) -> int:
        return self._scale

    @property
    def as_float(self) -> float:
        return self._value / (10 ** self._scale)

    @property
    def as_decimal(self) -> Decimal:
        return Decimal(str(self._value)) / Decimal(10 ** self._scale)

    @classmethod
    def from_decimal(cls, value: Decimal, currency: str, scale: int = 2) -> Money:
        cents = int(value * Decimal(10 ** scale))
        return cls(cents, currency, scale)

    @classmethod
    def from_float(cls, value: float, currency: str, scale: int = 2) -> Money:
        return cls(int(round(value * (10 ** scale))), currency, scale)

    @classmethod
    def from_string(cls, value: str, currency: str, scale: int = 2) -> Money:
        return cls.from_decimal(Decimal(value), currency, scale)

    def to_string(self) -> str:
        """Return money as string like '85000.00' for API responses."""
        d = Decimal(str(self._value)) / Decimal(10 ** self._scale)
        return f"{d:.{self._scale}f}"

    def to_display(self) -> str:
        return f"{self._value:,.{self._scale}f} {self._currency}"

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self._currency != other._currency:
            raise ValueError("Cannot add different currencies")
        return Money(self._value + other._value, self._currency, self._scale)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self._currency != other._currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self._value - other._value, self._currency, self._scale)

    def __mul__(self, factor: int | float | Decimal) -> "Money":
        result = int(self._value * Decimal(str(factor)))
        return Money(result, self._currency, self._scale)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self._value == other._value
                and self._currency == other._currency
                and self._scale == other._scale)

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._value < other._value

    def __le__(self, other: "Money") -> bool:
        return self == other or self < other

    def __gt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._value > other._value

    def __ge__(self, other: "Money") -> bool:
        return self == other or self > other

    def __hash__(self) -> int:
        return hash((self._value, self._currency, self._scale))

    def __repr__(self) -> str:
        return f"Money({self._value}, '{self._currency}', {self._scale})"


# ── Timestamp ──────────────────────────────────────────
class Timestamp:
    """Representa una fecha/hora estricta."""

    __slots__ = ("_value",)

    def __init__(self, value: datetime | str):
        if isinstance(value, str):
            self._value = datetime.fromisoformat(value)
        else:
            self._value = value

    @property
    def value(self) -> datetime:
        return self._value

    def to_iso(self) -> str:
        return self._value.isoformat()

    def to_date_string(self) -> str:
        return self._value.strftime("%Y-%m-%d")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Timestamp):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"Timestamp('{self._value.isoformat()}')"


# ── Account types ─────────────────────────────────────
class AccountType:
    BANK = "bank"
    CASH = "cash"
    DIGITAL_WALLET = "digital_wallet"
    CREDIT_CARD = "credit_card"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    OTHER = "other"

    # Nature mapping: asset or liability
    NATURE = {
        BANK: "asset",
        CASH: "asset",
        DIGITAL_WALLET: "asset",
        SAVINGS: "asset",
        INVESTMENT: "asset",
        CREDIT_CARD: "liability",
        OTHER: "asset",
    }

    @classmethod
    def get_nature(cls, account_type: str) -> str:
        return cls.NATURE.get(account_type, "asset")


# ── Transaction types ──────────────────────────────────
class TransactionType:
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


# ── Transaction statuses ───────────────────────────────
class TransactionStatus:
    PENDING = "pending"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


# ── Account ────────────────────────────────────────────
@dataclass
class Account:
    name: str
    account_type: str
    currency: str
    household_id: str
    balance: Money
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    member_id: Optional[str] = None
    account_number: Optional[str] = None
    status: str = "active"
    initial_balance: Money = field(default_factory=lambda: Money(0, "COP", 2))
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))
    updated_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))

    @property
    def nature(self) -> str:
        return AccountType.get_nature(self.account_type)


# ── Category ───────────────────────────────────────────
@dataclass
class Category:
    name: str
    type: str  # income, expense, both
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Transaction ────────────────────────────────────────
@dataclass
class Transaction:
    type: str  # income, expense
    account_id: str
    category_id: str
    amount: Money
    date: Timestamp
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    member_id: Optional[str] = None
    description: Optional[str] = None
    status: str = "processed"
    reference: Optional[str] = None
    notes: Optional[str] = None
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))
    updated_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))

    @property
    def amount_display(self) -> str:
        return self.amount.to_display()

    def __repr__(self) -> str:
        return f"Transaction(id={self.id}, type={self.type}, amount={self.amount_display})"


# ── Transfer ───────────────────────────────────────────
@dataclass
class Transfer:
    from_account_id: str
    to_account_id: str
    amount: Money
    date: Timestamp
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None
    reference: Optional[str] = None
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Budget ──────────────────────────────────────────────
@dataclass
class Budget:
    household_id: str
    category_id: str
    amount: Money
    period: str  # monthly, weekly, yearly
    year: int
    month: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spent: Money = field(default_factory=lambda: Money(0, "COP", 2))
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))

    @property
    def remaining(self) -> Money:
        return self.amount - self.spent

    @property
    def percentage(self) -> float:
        if self.amount.value == 0:
            return 0.0
        return float(self.spent.value / self.amount.value * 100)

    @property
    def status(self) -> str:
        pct = self.percentage
        if pct >= 100:
            return "exceeded"
        if pct >= 80:
            return "warning"
        return "healthy"


# ── RecurringPayment ───────────────────────────────────
@dataclass
class RecurringPayment:
    name: str
    amount: Money
    frequency: str  # monthly, weekly, yearly, biweekly
    category_id: str
    account_id: str
    household_id: str
    day_of_month: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    next_due_date: Optional[Timestamp] = None
    is_active: bool = True
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Debt ────────────────────────────────────────────────
@dataclass
class Debt:
    name: str
    principal: Money
    interest_rate: Decimal
    monthly_payment: Money
    currency: str
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creditor: Optional[str] = None
    installments: Optional[int] = None
    start_date: Optional[Timestamp] = None
    due_date: Optional[Timestamp] = None
    status: str = "active"
    balance: Money = field(default_factory=lambda: Money(0, "COP", 2))
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))

    def __post_init__(self):
        if self.balance.value == 0 and self.principal.value > 0:
            self.balance = self.principal


# ── DebtPayment ────────────────────────────────────────
@dataclass
class DebtPayment:
    debt_id: str
    amount: Money
    date: Timestamp
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Goal ────────────────────────────────────────────────
@dataclass
class Goal:
    name: str
    target_amount: Money
    household_id: str
    currency: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_date: Optional[Timestamp] = None
    current_amount: Money = field(default_factory=lambda: Money(0, "COP", 2))
    is_completed: bool = False
    is_active: bool = True
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))

    @property
    def progress(self) -> float:
        if self.target_amount.value == 0:
            return 0.0
        return float(self.current_amount.value / self.target_amount.value * 100)


# ── GoalContribution ───────────────────────────────────
@dataclass
class GoalContribution:
    goal_id: str
    amount: Money
    date: Timestamp
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Asset ───────────────────────────────────────────────
@dataclass
class Asset:
    name: str
    value: Money
    currency: str
    household_id: str
    acquired_date: Timestamp
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Liability ───────────────────────────────────────────
@dataclass
class Liability:
    name: str
    amount: Money
    currency: str
    household_id: str
    due_date: Timestamp
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creditor: Optional[str] = None
    interest_rate: Optional[Decimal] = None
    description: Optional[str] = None
    is_debt: bool = True
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Member ──────────────────────────────────────────────
@dataclass
class Member:
    name: str
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "adult"
    status: str = "active"
    email: Optional[str] = None
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Household ───────────────────────────────────────────
@dataclass
class Household:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    country: str = "CO"
    currency: str = "COP"
    timezone: str = "America/Bogota"
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))
    updated_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── User ────────────────────────────────────────────────
@dataclass
class User:
    name: str
    email: str
    password_hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    household_id: Optional[str] = None
    is_active: bool = True
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── Session ────────────────────────────────────────────
@dataclass
class Session:
    id: str
    user_id: str
    household_id: str
    expires_at: Timestamp
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))
    is_active: bool = True


# ── Notification ────────────────────────────────────────
@dataclass
class Notification:
    title: str
    message: str
    type: str  # warning, info, success, error
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    is_read: bool = False
    link: Optional[str] = None
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))


# ── LedgerEntry ────────────────────────────────────────
@dataclass
class LedgerEntry:
    transaction_id: str
    account_id: str
    type: str  # income, expense, transfer
    amount: Money
    balance_before: Money
    balance_after: Money
    household_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Timestamp = field(default_factory=lambda: Timestamp(datetime.now()))
