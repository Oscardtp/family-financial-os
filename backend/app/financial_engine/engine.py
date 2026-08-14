"""Financial Engine - Pure computation functions (no I/O).

Funciones puras que realizan cálculos financieros.

Este módulo es independiente de HTTP, SQLite, HTML, y JavaScript.

Se recomienda la dependencia `python-money` para tipos Money
pero se puede implementar desde cero sin dependencias externas.

Todo se representa como entero en la unidad menor (centavos) del COP.
Redondeos siempre con ROUND_HALF_UP.
"""

from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import List, Optional

from app.domain.domain import Money, Timestamp, Account, AccountType, Transaction, TransactionType, TransactionStatus, Budget, Debt, Goal, Asset, Liability, Member, Household


# ── Money helpers ──────────────────────────────

def money_from_int(value: int, currency: str, scale: int = 2) -> Money:
    return Money(value, currency, scale)


def money_from_float(value: float, currency: str, scale: int = 2) -> Money:
    return Money(int(round(value * (10 ** scale))), currency, scale)


def money_display(value: Money) -> str:
    return f"{value._value:,.{value._scale}f} {value._currency}"


# ── Cash flow ──────────────────────────────────

def cash_flow(income: Money, expenses: Money) -> Decimal:
    """Flujo de caja: ingreso - gasto como Decimal."""
    return Decimal(income.value) - Decimal(expenses.value)


def savings_rate(income: Money, expenses: Money) -> Decimal:
    """Tasa de ahorro como Decimal."""
    if income.value == 0:
        return Decimal("0")
    return Decimal(income.value - expenses.value) / Decimal(income.value)


def net_worth(assets: List[Money], liabilities: List[Money]) -> Decimal:
    """Patrimonio neto: activos - pasivos."""
    return sum(Decimal(a.value) for a in assets) - sum(Decimal(l.value) for l in liabilities)


def debt_balance(debts: List[Debt]) -> Decimal:
    """Saldo total de deudas."""
    return sum(Decimal(d.balance.value) for d in debts)


def goal_progress(goal: Goal) -> Decimal:
    """Progreso del objetivo 0-1."""
    if goal.target_amount.value == 0:
        return Decimal("0")
    return Decimal(goal.current_amount.value) / Decimal(goal.target_amount.value)


def monthly_projection(income: Money, expenses: Money) -> Decimal:
    """Proyección mensual."""
    return Decimal(income.value) - Decimal(expenses.value)


# ── Money calculations ─────────────────────────

def apply_discount(amount: Money, discount_pct: Decimal) -> Money:
    """Aplica descuento a un monto."""
    if discount_pct < 0 or discount_pct > 1:
        raise ValueError("discount_pct must be between 0 and 1")
    factor = Decimal("1") - discount_pct
    return Money(int(amount.value * factor), amount.currency, amount.scale)


def apply_tax(amount: Money, tax_rate: Decimal) -> Money:
    """Aplica impuesto a un monto."""
    if tax_rate < 0:
        raise ValueError("tax_rate cannot be negative")
    factor = Decimal("1") + tax_rate
    return Money(int(amount.value * factor), amount.currency, amount.scale)


def clamp(value: Decimal, min_val: Decimal, max_val: Decimal) -> Decimal:
    return max(min(value, max_val), min_val)


def round_to_scale(value: Decimal, scale: int) -> Decimal:
    return value.quantize(Decimal("1." + "0" * scale), rounding=ROUND_HALF_UP)


# ── Transacciones: dinero entre cuentas ───────

def transfer_amount(from_amount: Money, to_amount: Money, fee_pct: Decimal = Decimal("0.01")):
    """Transferencia con comisión."""
    fee = Money(int(round(from_amount.value * fee_pct)), from_amount.currency, from_amount.scale)
    return from_amount - fee, to_amount + fee


# ── Presupuesto ────────────────────────────────

def budget_status(budget: Budget, actual_spend: Money) -> str:
    """Evalúa estado del presupuesto: HEALTHY / WARNING / EXCEEDED."""
    if actual_spend > budget.amount:
        return "EXCEEDED"
    if actual_spend > budget.amount * Decimal("0.8"):
        return "WARNING"
    return "HEALTHY"


# ── Deuda ──────────────────────────────────────

def debt_payoff_status(debt: Debt, payment_made: Money) -> str:
    """Estado de la deuda: PAYED / IN_DEBT."""
    remaining = debt.balance - payment_made
    if remaining <= Money(0, debt.currency, 2):
        return "PAYED"
    return "IN_DEBT"


def debt_total_interest(debt: Debt, months: int) -> Decimal:
    """Interés acumulado en N meses."""
    return Decimal(debt.principal.value * debt.interest_rate * months / 12)