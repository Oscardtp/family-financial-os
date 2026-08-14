"""Tests for Family Financial OS."""

from __future__ import annotations
import pytest
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from app.domain import (
    Money, Timestamp, Account, AccountType, Transaction,
    TransactionType, TransactionStatus, Budget, Debt, Goal,
    Asset, Liability, Member, Household
)
from app.financial_engine import (
    cash_flow, savings_rate, net_worth, debt_balance,
    goal_progress, monthly_projection, apply_discount,
    apply_tax, round_to_scale, clamp, transfer_amount,
    budget_status, debt_payoff_status, debt_total_interest
)


# ── Money ─────────────────────────────────────

def test_money_from_int():
    m = Money(1000, "COP", 2)
    assert m.value == 1000
    assert m.currency == "COP"
    assert m.scale == 2
    assert m.as_float == 10.00
    assert m.to_display() == "1,000.00 COP"


def test_money_from_float():
    m = Money.from_float(12.34, "COP", 2)
    assert m.value == 1234
    assert m.as_float == 12.34


def test_money_negative_raises():
    with pytest.raises(ValueError):
        Money(-100, "COP", 2)


def test_money_equality():
    a = Money(1000, "COP", 2)
    b = Money(1000, "COP", 2)
    assert a == b


def test_money_hash():
    m1 = Money(1000, "COP", 2)
    m2 = Money(1000, "COP", 2)
    assert hash(m1) == hash(m2)


# ── Timestamp ─────────────────────────────────

def test_timestamp_from_iso():
    t = Timestamp("2024-01-15T10:30:00")
    assert t.value.year == 2024
    assert t.value.month == 1
    assert t.value.day == 15


def test_timestamp_to_iso():
    t = Timestamp(datetime(2024, 1, 15, 10, 30, 0))
    assert t.to_iso() == "2024-01-15T10:30:00"


# ── Financial Engine ──────────────────────────────

def test_cash_flow_positive():
    income = Money(20000, "COP", 2)
    expenses = Money(10000, "COP", 2)
    assert cash_flow(income, expenses) == Decimal(10000)


def test_cash_flow_negative():
    income = Money(10000, "COP", 2)
    expenses = Money(15000, "COP", 2)
    assert cash_flow(income, expenses) == Decimal(-5000)


def test_cash_flow_zero_income():
    assert cash_flow(Money(0, "COP", 2), Money(5000, "COP", 2)) == Decimal(-5000)


def test_cash_flow_zero_expenses():
    assert cash_flow(Money(5000, "COP", 2), Money(0, "COP", 2)) == Decimal(5000)


def test_cash_flow_both_zero():
    assert cash_flow(Money(0, "COP", 2), Money(0, "COP", 2)) == Decimal(0)


def test_savings_rate():
    assert savings_rate(Money(20000, "COP", 2), Money(12000, "COP", 2)) == Decimal("0.4")


def test_savings_rate_zero():
    assert savings_rate(Money(0, "COP", 2), Money(0, "COP", 2)) == Decimal("0")


def test_savings_rate_zero_expenses():
    assert savings_rate(Money(10000, "COP", 2), Money(0, "COP", 2)) == Decimal("1")


def test_savings_rate_zero_income():
    assert savings_rate(Money(0, "COP", 2), Money(10000, "COP", 2)) == Decimal("0")


def test_net_worth():
    assets = [Money(100000, "COP", 2), Money(50000, "COP", 2)]
    liabilities = [Money(30000, "COP", 2)]
    assert net_worth(assets, liabilities) == Decimal(120000)


def test_net_worth_empty():
    assert net_worth([], []) == Decimal(0)


def test_net_worth_only_assets():
    assets = [Money(100000, "COP", 2)]
    assert net_worth(assets, []) == Decimal(100000)


def test_net_worth_only_liabilities():
    liabilities = [Money(30000, "COP", 2)]
    assert net_worth([], liabilities) == Decimal(-30000)


def test_debt_balance():
    debts = [Debt(id="1", name="Loan", principal=Money(100000, "COP", 2),
                  interest_rate=Decimal("0.05"), monthly_payment=Money(2000, "COP", 2),
                  household_id="h", currency="COP", due_date=Timestamp("2024-01-01"),
                  status="ACTIVE", created_at=Timestamp(datetime.now()))]
    assert debt_balance(debts) == Decimal(100000)


def test_goal_progress():
    goal = Goal(id="1", name="Ahorro", target_amount=Money(100000, "COP", 2),
                household_id="h", currency="COP",
                current_amount=Money(50000, "COP", 2),
                is_completed=False, is_active=True)
    assert goal_progress(goal) == Decimal("0.5")


def test_monthly_projection():
    income = Money(50000, "COP", 2)
    expenses = Money(30000, "COP", 2)
    assert monthly_projection(income, expenses) == Decimal(20000)


def test_apply_discount():
    amount = Money(10000, "COP", 2)
    discounted = apply_discount(amount, Decimal("0.10"))
    assert discounted.value == 9000
    assert discounted.currency == "COP"


def test_apply_discount_zero_discount():
    amount = Money(10000, "COP", 2)
    result = apply_discount(amount, Decimal("0"))
    assert result.value == 10000


def test_apply_discount_full():
    amount = Money(10000, "COP", 2)
    result = apply_discount(amount, Decimal("1"))
    assert result.value == 0


def test_apply_discount_negative_raises():
    amount = Money(10000, "COP", 2)
    with pytest.raises(ValueError):
        apply_discount(amount, Decimal("-0.1"))


def test_apply_discount_over_one_raises():
    amount = Money(10000, "COP", 2)
    with pytest.raises(ValueError):
        apply_discount(amount, Decimal("1.1"))


def test_apply_tax():
    amount = Money(10000, "COP", 2)
    taxed = apply_tax(amount, Decimal("0.19"))
    assert taxed.value == 11900


def test_apply_tax_zero():
    amount = Money(10000, "COP", 2)
    result = apply_tax(amount, Decimal("0"))
    assert result.value == 10000


def test_apply_tax_negative_raises():
    amount = Money(10000, "COP", 2)
    with pytest.raises(ValueError):
        apply_tax(amount, Decimal("-0.1"))


def test_apply_tax_10_percent():
    amount = Money(10000, "COP", 2)
    result = apply_tax(amount, Decimal("0.10"))
    assert result.value == 11000


def test_round_to_scale():
    value = Decimal("10.12345")
    rounded = round_to_scale(value, 2)
    assert rounded == Decimal("10.12")


def test_clamp():
    assert clamp(Decimal("10"), Decimal("0"), Decimal("100")) == Decimal("10")
    assert clamp(Decimal("150"), Decimal("0"), Decimal("100")) == Decimal("100")


def test_money_display():
    m = Money(5000, "COP", 2)
    assert m.to_display() == "5,000.00 COP"


def test_savings_rate_with_zero_income():
    assert savings_rate(Money(0, "COP", 2), Money(0, "COP", 2)) == Decimal("0")


def test_budget_status_healthy():
    budget = Budget(id="1", household_id="h", category_id="cat",
                    amount=Money(100000, "COP", 2), period="monthly", year=2026,
                    spent=Money(50000, "COP", 2))
    assert budget_status(budget, Money(50000, "COP", 2)) == "HEALTHY"


def test_budget_status_warning():
    budget = Budget(id="1", household_id="h", category_id="cat",
                    amount=Money(100000, "COP", 2), period="monthly", year=2026,
                    spent=Money(80000, "COP", 2))
    assert budget_status(budget, Money(85000, "COP", 2)) == "WARNING"


def test_budget_status_exceeded():
    budget = Budget(id="1", household_id="h", category_id="cat",
                    amount=Money(100000, "COP", 2), period="monthly", year=2026,
                    spent=Money(100000, "COP", 2))
    assert budget_status(budget, Money(100001, "COP", 2)) == "EXCEEDED"


def test_debt_payoff_status_payed():
    debt = Debt(id="1", name="Loan", principal=Money(100000, "COP", 2),
                interest_rate=Decimal("0.05"), monthly_payment=Money(2000, "COP", 2),
                household_id="h", currency="COP", due_date=Timestamp("2024-01-01"),
                status="ACTIVE", created_at=Timestamp(datetime.now()))
    assert debt_payoff_status(debt, Money(100000, "COP", 2)) == "PAYED"


def test_debt_payoff_status_in_debt():
    debt = Debt(id="1", name="Loan", principal=Money(100000, "COP", 2),
                interest_rate=Decimal("0.05"), monthly_payment=Money(2000, "COP", 2),
                household_id="h", currency="COP", due_date=Timestamp("2024-01-01"),
                status="ACTIVE", created_at=Timestamp(datetime.now()))
    assert debt_payoff_status(debt, Money(50000, "COP", 2)) == "IN_DEBT"


def test_debt_total_interest():
    debt = Debt(id="1", name="Loan", principal=Money(100000, "COP", 2),
                interest_rate=Decimal("0.05"), monthly_payment=Money(2000, "COP", 2),
                household_id="h", currency="COP", due_date=Timestamp("2024-01-01"),
                status="ACTIVE", created_at=Timestamp(datetime.now()))
    interest = debt_total_interest(debt, 12)
    assert interest == Decimal("5000.00")


def test_transfer_amount_with_fee():
    from_m = Money(10000, "COP", 2)
    to_m = Money(5000, "COP", 2)
    new_from, new_to = transfer_amount(from_m, to_m, Decimal("0.01"))
    assert new_from.value == 9900
    assert new_to.value == 5100


def test_transfer_amount_no_fee():
    from_m = Money(10000, "COP", 2)
    to_m = Money(5000, "COP", 2)
    new_from, new_to = transfer_amount(from_m, to_m, Decimal("0"))
    assert new_from.value == 10000
    assert new_to.value == 5000