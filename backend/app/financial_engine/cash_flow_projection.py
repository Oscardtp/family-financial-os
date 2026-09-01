from datetime import date, datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class CashFlowProjection:
    available_balance: Decimal
    pending_payments: Decimal
    expected_income: Decimal
    projected_balance: Decimal
    events_7_days: list[dict]
    events_30_days: list[dict]


class CashFlowProjectionEngine:

    def project(self, balance: Decimal, events: list[dict], today: date = None) -> CashFlowProjection:
        if today is None:
            today = date.today()

        in_7 = today + timedelta(days=7)
        in_30 = today + timedelta(days=30)

        payments_7 = []
        payments_30 = []
        income_7 = Decimal("0")
        income_30 = Decimal("0")
        total_pending = Decimal("0")

        for e in events:
            if e["status"] != "pending":
                continue

            due = e["due_date"]
            if isinstance(due, str):
                due = date.fromisoformat(due)

            amount = Decimal(str(e["amount"]))
            is_income = e.get("type") == "income"

            if today <= due <= in_30:
                if is_income:
                    income_30 += amount
                    if due <= in_7:
                        income_7 += amount
                else:
                    payments_30.append(e)
                    total_pending += amount
                    if due <= in_7:
                        payments_7.append(e)

        return CashFlowProjection(
            available_balance=balance,
            pending_payments=total_pending,
            expected_income=income_30,
            projected_balance=balance + income_30 - total_pending,
            events_7_days=payments_7,
            events_30_days=payments_30,
        )
