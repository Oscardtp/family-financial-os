"""Tests for Family Financial OS - Domain layer."""

from __future__ import annotations
import pytest
from datetime import datetime
from decimal import Decimal

from app.domain import (
    Money, Timestamp, Account, AccountType, Transaction,
    TransactionType, TransactionStatus, Budget, Debt, Goal,
    Asset, Liability, Member, Household, Transfer
)
from app.financial_engine import (
    cash_flow, savings_rate, net_worth, debt_balance,
    goal_progress, monthly_projection, apply_discount,
    apply_tax, round_to_scale, clamp, transfer_amount,
    budget_status, debt_payoff_status, debt_total_interest
)


# ── Money tests ──────────────────────────────────

def test_money_creation():
    m = Money(1000, "COP", 2)
    assert m.value == 1000
    assert m.currency == "COP"
    assert m.scale == 2


def test_money_display():
    m = Money(5000, "COP", 2)
    assert m.to_display() == "5,000.00 COP"


def test_money_equality():
    a = Money(1000, "COP", 2)
    b = Money(1000, "COP", 2)
    assert a == b
    c = Money(1000, "COP", 3)
    assert a != c


def test_money_negative_raises():
    with pytest.raises(ValueError):
        Money(-100, "COP", 2)


def test_money_add_same_currency():
    a = Money(1000, "COP", 2)
    b = Money(2000, "COP", 2)
    result = a + b
    assert result.value == 3000
    assert result.currency == "COP"


def test_money_add_different_currency_raises():
    a = Money(1000, "COP", 2)
    b = Money(1000, "USD", 2)
    with pytest.raises(ValueError):
        a + b


def test_money_sub_same_currency():
    a = Money(5000, "COP", 2)
    b = Money(2000, "COP", 2)
    result = a - b
    assert result.value == 3000


def test_money_sub_different_currency_raises():
    a = Money(5000, "COP", 2)
    b = Money(2000, "USD", 2)
    with pytest.raises(ValueError):
        a - b


def test_money_mul_int():
    m = Money(1000, "COP", 2)
    result = m * 2
    assert result.value == 2000


def test_money_mul_float():
    m = Money(1000, "COP", 2)
    result = m * 1.5
    assert result.value == 1500


def test_money_mul_decimal():
    m = Money(1000, "COP", 2)
    result = m * Decimal("0.5")
    assert result.value == 500


def test_money_mul_zero():
    m = Money(1000, "COP", 2)
    result = m * 0
    assert result.value == 0


def test_money_from_string():
    m = Money.from_string("12.34", "COP", 2)
    assert m.value == 1234


def test_money_from_string_decimal():
    m = Money.from_string("99.99", "COP", 2)
    assert m.value == 9999


def test_money_to_string():
    m = Money(85000, "COP", 2)
    assert m.to_string() == "850.00"


def test_money_as_float():
    m = Money(1234, "COP", 2)
    assert m.as_float == 12.34


def test_money_as_decimal():
    m = Money(1234, "COP", 2)
    assert m.as_decimal == Decimal("12.34")


def test_money_comparison():
    a = Money(1000, "COP", 2)
    b = Money(2000, "COP", 2)
    assert a < b
    assert b > a
    assert a <= a
    assert a >= a


# ── Account type tests ──────────────────────────

def test_account_type_asset_nature():
    assert AccountType.get_nature(AccountType.BANK) == "asset"
    assert AccountType.get_nature(AccountType.CASH) == "asset"
    assert AccountType.get_nature(AccountType.DIGITAL_WALLET) == "asset"


def test_account_type_liability_nature():
    assert AccountType.get_nature(AccountType.CREDIT_CARD) == "liability"


def test_account_type_default_nature():
    assert AccountType.get_nature("unknown_type") == "asset"


def test_account_nature_property():
    account = Account(name="Test", account_type=AccountType.CREDIT_CARD, currency="COP", household_id="h", balance=Money(0, "COP", 2))
    assert account.nature == "liability"


# ── Budget tests ────────────────────────────────

def test_budget_remaining():
    budget = Budget(id="1", household_id="h", category_id="cat",
                    amount=Money(100000, "COP", 2), period="monthly", year=2026,
                    spent=Money(40000, "COP", 2))
    assert budget.remaining == Money(60000, "COP", 2)


def test_budget_percentage():
    budget = Budget(id="1", household_id="h", category_id="cat",
                    amount=Money(100000, "COP", 2), period="monthly", year=2026,
                    spent=Money(25000, "COP", 2))
    assert budget.percentage == 25.0


def test_budget_percentage_zero_amount():
    budget = Budget(id="1", household_id="h", category_id="cat",
                    amount=Money(0, "COP", 2), period="monthly", year=2026,
                    spent=Money(0, "COP", 2))
    assert budget.percentage == 0.0


# ── Debt tests ───────────────────────────────────

def test_debt_balance_initialization():
    debt = Debt(id="1", name="Loan", principal=Money(100000, "COP", 2),
                interest_rate=Decimal("0.05"), monthly_payment=Money(2000, "COP", 2),
                household_id="h", currency="COP", due_date=Timestamp("2024-01-01"),
                status="ACTIVE", created_at=Timestamp(datetime.now()))
    assert debt.balance.value == 100000


def test_debt_balance_zero_principal():
    debt = Debt(id="1", name="Loan", principal=Money(0, "COP", 2),
                interest_rate=Decimal("0.05"), monthly_payment=Money(0, "COP", 2),
                household_id="h", currency="COP", due_date=Timestamp("2024-01-01"),
                status="ACTIVE", created_at=Timestamp(datetime.now()))
    assert debt.balance.value == 0


# ── Goal tests ───────────────────────────────────

def test_goal_progress_zero_current():
    goal = Goal(id="1", name="Ahorro", target_amount=Money(100000, "COP", 2),
                household_id="h", currency="COP",
                current_amount=Money(0, "COP", 2),
                is_completed=False, is_active=True)
    assert goal_progress(goal) == Decimal("0")


def test_goal_progress_exceeded():
    goal = Goal(id="1", name="Ahorro", target_amount=Money(100000, "COP", 2),
                household_id="h", currency="COP",
                current_amount=Money(150000, "COP", 2),
                is_completed=False, is_active=True)
    assert goal_progress(goal) == Decimal("1.5")


# ── Timestamp tests ──────────────────────────────

def test_timestamp_from_iso():
    t = Timestamp("2024-01-15T10:30:00")
    assert t.value.year == 2024
    assert t.value.month == 1
    assert t.value.day == 15


def test_timestamp_to_iso():
    t = Timestamp(datetime(2024, 1, 15, 10, 30, 0))
    assert t.to_iso() == "2024-01-15T10:30:00"


def test_timestamp_to_date_string():
    t = Timestamp(datetime(2024, 1, 15, 10, 30, 0))
    assert t.to_date_string() == "2024-01-15"

# ── Domain tests ─────────────────────────────────

def test_budget_status_healthy():
    budget = Budget(id="1", household_id="h", category_id="cat",
                    amount=Money(80000, "COP", 2), period="monthly", year=2026,
                    spent=Money(60000, "COP", 2))
    assert budget.status == "healthy"


def test_budget_status_warning():
    budget = Budget(id="2", household_id="h", category_id="cat",
                    amount=Money(80000, "COP", 2), period="monthly", year=2026,
                    spent=Money(65000, "COP", 2))
    assert budget.status == "warning"


def test_budget_status_exceeded():
    budget = Budget(id="3", household_id="h", category_id="cat",
                    amount=Money(80000, "COP", 2), period="monthly", year=2026,
                    spent=Money(90000, "COP", 2))
    assert budget.status == "exceeded"


def test_budget_status_with_80_percent():
    budget = Budget(id="4", household_id="h", category_id="cat",
                    amount=Money(100000, "COP", 2), period="monthly", year=2026,
                    spent=Money(80000, "COP", 2))
    assert budget.status == "warning"


def test_debt_balance():
    debt = Debt(id="1", name="Loan", principal=Money(100000, "COP", 2),
                interest_rate=Decimal("0.05"), monthly_payment=Money(2000, "COP", 2),
                household_id="h", currency="COP", due_date=Timestamp("2024-01-01"),
                status="ACTIVE", created_at=Timestamp(datetime.now()))
    assert debt.balance.value == 100000


def test_goal_progress():
    goal = Goal(id="1", name="Ahorro", target_amount=Money(100000, "COP", 2),
                household_id="h", currency="COP",
                current_amount=Money(50000, "COP", 2),
                is_completed=False, is_active=True)
    assert goal_progress(goal) == Decimal("0.5")


def test_goal_progress_full():
    goal = Goal(id="2", name="Ahorro", target_amount=Money(100000, "COP", 2),
                household_id="h", currency="COP",
                current_amount=Money(100000, "COP", 2),
                is_completed=False, is_active=True)
    assert goal_progress(goal) == Decimal("1")


def test_goal_progress_zero_target():
    goal = Goal(id="3", name="Ahorro", target_amount=Money(0, "COP", 2),
                household_id="h", currency="COP",
                current_amount=Money(0, "COP", 2),
                is_completed=False, is_active=True)
    assert goal_progress(goal) == Decimal("0")


def test_cash_flow_positive():
    assert cash_flow(Money(20000, "COP", 2), Money(10000, "COP", 2)) == Decimal(10000)


def test_cash_flow_negative():
    assert cash_flow(Money(10000, "COP", 2), Money(15000, "COP", 2)) == Decimal(-5000)


def test_savings_rate():
    assert savings_rate(Money(20000, "COP", 2), Money(12000, "COP", 2)) == Decimal("0.4")


def test_savings_rate_zero():
    assert savings_rate(Money(0, "COP", 2), Money(0, "COP", 2)) == Decimal("0")


def test_net_worth_positive():
    assets = [Money(100000, "COP", 2), Money(50000, "COP", 2)]
    liabilities = [Money(30000, "COP", 2)]
    assert net_worth(assets, liabilities) == Decimal(120000)


def test_net_worth_empty():
    assert net_worth([], []) == Decimal(0)


def test_monthly_projection():
    assert monthly_projection(Money(50000, "COP", 2), Money(30000, "COP", 2)) == Decimal(20000)


def test_apply_discount():
    amount = Money(10000, "COP", 2)
    discounted = apply_discount(amount, Decimal("0.10"))
    assert discounted.value == 9000


def test_apply_tax():
    amount = Money(10000, "COP", 2)
    taxed = apply_tax(amount, Decimal("0.19"))
    assert taxed.value == 11900


def test_round_to_scale():
    value = Decimal("10.12345")
    rounded = round_to_scale(value, 2)
    assert rounded == Decimal("10.12")


def test_clamp():
    assert clamp(Decimal("10"), Decimal("0"), Decimal("100")) == Decimal("10")
    assert clamp(Decimal("150"), Decimal("0"), Decimal("100")) == Decimal("100")


def test_money_from_float():
    m = Money.from_float(12.34, "COP", 2)
    assert m.value == 1234
    assert m.as_float == 12.34
