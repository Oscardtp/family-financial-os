import uuid
from datetime import datetime, date, timezone
from decimal import Decimal
from dataclasses import dataclass, field
from app.domain.value_objects.money import Money


@dataclass
class User:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
    name: str = ""
    password_hash: str = ""
    role: str = "member"
    household_id: uuid.UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Account:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    type: str = "cash"
    balance: Money = field(default_factory=lambda: Money.zero())
    currency: str = "COP"
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Category:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    type: str = "expense"
    icon: str | None = None
    color: str | None = None


@dataclass
class Transaction:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    account_id: uuid.UUID = field(default_factory=uuid.uuid4)
    category_id: uuid.UUID | None = None
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    type: str = "expense"
    amount: Money = field(default_factory=lambda: Money.zero())
    description: str = ""
    date: date = field(default_factory=date.today)
    to_account_id: uuid.UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Budget:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    category_id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    amount: Money = field(default_factory=lambda: Money.zero())
    month: int = 0
    year: int = 0


@dataclass
class Debt:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    creditor: str = ""
    total_amount: Money = field(default_factory=lambda: Money.zero())
    current_balance: Money = field(default_factory=lambda: Money.zero())
    interest_rate: Decimal = Decimal("0.00")
    minimum_payment: Money = field(default_factory=lambda: Money.zero())
    due_day: int = 1
    start_date: date | None = None
    end_date: date | None = None
    status: str = "active"


@dataclass
class DebtPayment:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    debt_id: uuid.UUID = field(default_factory=uuid.uuid4)
    amount: Money = field(default_factory=lambda: Money.zero())
    principal: Money = field(default_factory=lambda: Money.zero())
    interest: Money = field(default_factory=lambda: Money.zero())
    payment_date: date = field(default_factory=date.today)


@dataclass
class SavingsGoal:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    target_amount: Money = field(default_factory=lambda: Money.zero())
    current_amount: Money = field(default_factory=lambda: Money.zero())
    target_date: date | None = None
    priority: str = "medium"


@dataclass
class SavingsContribution:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    goal_id: uuid.UUID = field(default_factory=uuid.uuid4)
    amount: Money = field(default_factory=lambda: Money.zero())
    contribution_date: date = field(default_factory=date.today)


@dataclass
class RecurringPayment:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    account_id: uuid.UUID = field(default_factory=uuid.uuid4)
    category_id: uuid.UUID | None = None
    name: str = ""
    amount: Money = field(default_factory=lambda: Money.zero())
    type: str = "expense"
    frequency: str = "monthly"
    day_of_month: int = 1
    next_due_date: date = field(default_factory=date.today)
    is_active: bool = True
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FinancialObligation:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    source: str = "USER"
    source_id: uuid.UUID | None = None
    name: str = ""
    type: str = "expense"
    amount: Money = field(default_factory=lambda: Money.zero())
    currency: str = "COP"
    frequency: str = "monthly"
    anchor_day: int | None = None
    recommended_offset_days: int = 5
    cutoff_offset_days: int | None = None
    reminder_days_before: int = 3
    account_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    responsible_member_id: uuid.UUID | None = None
    is_active: bool = True
    confidence: int = 100
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FinancialEvent:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    source: str = "USER"
    source_id: uuid.UUID | None = None
    type: str = "expense"
    title: str = ""
    amount: Money = field(default_factory=lambda: Money.zero())
    currency: str = "COP"
    due_date: date = field(default_factory=date.today)
    recommended_date: date | None = None
    cutoff_date: date | None = None
    status: str = "pending"
    account_id: uuid.UUID | None = None
    responsible_member_id: uuid.UUID | None = None
    is_recurrent: bool = False
    recurrence_group_id: uuid.UUID | None = None
    reminder_days_before: int = 3
    notes: str | None = None
    confirmed: bool = True
    paid_at: datetime | None = None
    paid_amount: Money | None = None
    paid_by: uuid.UUID | None = None
    obligation_id: uuid.UUID | None = None
    visibility: str = "confirmed"
    confidence: int = 100
    payment_method: str | None = None
    consequence_note: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Asset:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    type: str = ""
    value: Money = field(default_factory=lambda: Money.zero())
    purchase_date: date | None = None


@dataclass
class Liability:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    household_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    type: str = ""
    total_amount: Money = field(default_factory=lambda: Money.zero())
    current_balance: Money = field(default_factory=lambda: Money.zero())
    interest_rate: Decimal = Decimal("0.00")
    monthly_payment: Money = field(default_factory=lambda: Money.zero())
