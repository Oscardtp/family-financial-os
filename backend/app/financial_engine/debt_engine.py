from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from app.domain.value_objects.money import Money
from app.financial_engine.money_operations import MoneyOperations


@dataclass
class DebtAmortizationRow:
    period: int
    payment: Money
    principal: Money
    interest: Money
    balance: Money


@dataclass
class DebtSummaryItem:
    id: str
    name: str
    creditor: str
    original_amount: Money
    current_balance: Money
    interest_rate: Decimal
    minimum_payment: Money
    paid_percentage: Decimal
    status: str


@dataclass
class DebtSummaryResult:
    items: list[DebtSummaryItem]
    total_original: Money
    total_balance: Money
    total_paid: Money
    overall_progress: Decimal


class DebtEngine:
    def calculate_summary(self, debts: list[dict]) -> DebtSummaryResult:
        items = []
        total_original = Money.zero()
        total_balance = Money.zero()

        for debt in debts:
            original = Money(Decimal(str(debt["total_amount"])))
            balance = Money(Decimal(str(debt["current_balance"])))
            paid = original - balance
            progress = MoneyOperations.percentage(paid, original) if not original.is_zero() else Decimal("0")

            if debt.get("status") == "paid":
                status = "paid"
            elif progress >= Decimal("75"):
                status = "almost_done"
            else:
                status = "active"

            items.append(DebtSummaryItem(
                id=str(debt["id"]),
                name=debt["name"],
                creditor=debt.get("creditor", ""),
                original_amount=original,
                current_balance=balance,
                interest_rate=Decimal(str(debt.get("interest_rate", 0))),
                minimum_payment=Money(Decimal(str(debt.get("minimum_payment", 0)))),
                paid_percentage=progress,
                status=status,
            ))

            total_original = total_original + original
            total_balance = total_balance + balance

        total_paid = total_original - total_balance
        overall_progress = MoneyOperations.percentage(total_paid, total_original) if not total_original.is_zero() else Decimal("0")

        return DebtSummaryResult(
            items=items,
            total_original=total_original,
            total_balance=total_balance,
            total_paid=total_paid,
            overall_progress=overall_progress,
        )

    def generate_amortization(
        self, balance: Money, annual_rate: Decimal, months: int
    ) -> list[DebtAmortizationRow]:
        rows = []
        current_balance = balance

        for period in range(1, months + 1):
            remaining_periods = months - period + 1
            amort = MoneyOperations.amortize_payment(current_balance, annual_rate, remaining_periods, 1)
            current_balance = amort["remaining"]

            rows.append(DebtAmortizationRow(
                period=period,
                payment=amort["payment"],
                principal=amort["principal"],
                interest=amort["interest"],
                balance=current_balance,
            ))

        return rows

    def project_payoff(
        self, balance: Money, annual_rate: Decimal, monthly_payment: Money
    ) -> dict:
        if monthly_payment.is_zero() or balance.is_zero():
            return {"months": 0, "total_paid": Money.zero(), "total_interest": Money.zero()}

        monthly_rate = (1 + annual_rate / Decimal("100")) ** (Decimal("1") / Decimal("12")) - 1
        current_balance = balance
        months = 0
        total_paid = Money.zero()

        while current_balance.is_positive() and months < 600:
            interest = Money(current_balance.amount * monthly_rate, balance.currency)
            principal = monthly_payment - interest

            if principal.amount > current_balance.amount:
                principal = current_balance
                payment = principal + interest
            else:
                payment = monthly_payment

            current_balance = current_balance - principal
            total_paid = total_paid + payment
            months += 1

            if current_balance.is_negative():
                current_balance = Money.zero()

        return {
            "months": months,
            "total_paid": total_paid,
            "total_interest": total_paid - balance,
        }
