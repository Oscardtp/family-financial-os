from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from app.domain.value_objects.money import Money


@dataclass
class AmortizationRow:
    month: int
    payment_date: str
    payment: Decimal
    principal: Decimal
    interest: Decimal
    balance: Decimal
    cumulative_interest: Decimal


@dataclass
class AmortizationSchedule:
    debt_name: str
    original_balance: Decimal
    interest_rate: Decimal
    monthly_payment: Decimal
    rows: list[AmortizationRow] = field(default_factory=list)
    total_interest: Decimal = Decimal("0")
    total_payments: Decimal = Decimal("0")
    payoff_months: int = 0
    payoff_date: str = ""


class AmortizationEngine:
    def generate_schedule(
        self,
        balance: Decimal,
        annual_rate: Decimal,
        monthly_payment: Decimal,
        debt_name: str = "",
        start_date: date | None = None,
    ) -> AmortizationSchedule:
        if monthly_payment <= 0 or balance <= 0:
            return AmortizationSchedule(
                debt_name=debt_name,
                original_balance=balance,
                interest_rate=annual_rate,
                monthly_payment=Decimal("0"),
            )

        monthly_rate = (1 + annual_rate / Decimal("100")) ** (Decimal("1") / Decimal("12")) - 1
        remaining = balance
        payment = monthly_payment
        schedule = AmortizationSchedule(
            debt_name=debt_name,
            original_balance=balance,
            interest_rate=annual_rate,
            monthly_payment=monthly_payment,
        )

        current_date = start_date or date.today()
        month_num = 0
        cumulative_interest = Decimal("0")

        while remaining > Decimal("0.01") and month_num < 600:
            month_num += 1
            interest_charge = (remaining * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            cumulative_interest += interest_charge

            if payment <= interest_charge:
                principal_portion = Decimal("0")
                actual_payment = interest_charge
            else:
                principal_portion = min(payment - interest_charge, remaining)
                actual_payment = principal_portion + interest_charge

            remaining -= principal_portion
            if remaining < 0:
                remaining = Decimal("0")

            next_date = current_date + timedelta(days=30)
            schedule.rows.append(AmortizationRow(
                month=month_num,
                payment_date=next_date.isoformat(),
                payment=actual_payment,
                principal=principal_portion,
                interest=interest_charge,
                balance=remaining,
                cumulative_interest=cumulative_interest,
            ))
            current_date = next_date

        schedule.total_interest = cumulative_interest
        schedule.total_payments = balance + cumulative_interest
        schedule.payoff_months = month_num
        if start_date:
            from dateutil.relativedelta import relativedelta
            schedule.payoff_date = (start_date + relativedelta(months=month_num)).isoformat()
        else:
            schedule.payoff_date = schedule.rows[-1].payment_date if schedule.rows else ""

        return schedule

    def calculate_due_alerts(
        self,
        debts: list[dict],
        today: date | None = None,
        paid_months: dict | None = None,
    ) -> list[dict]:
        today = today or date.today()
        paid_months = paid_months or {}
        alerts = []
        for debt in debts:
            due_day = debt.get("due_day", 1)
            status = debt.get("status", "active")
            if status != "active":
                continue

            debt_id = debt["id"]
            current_paid = paid_months.get(debt_id, set())
            current_month_key = (today.year, today.month)
            if current_month_key in current_paid:
                continue

            try:
                due_date = date(today.year, today.month, due_day)
            except ValueError:
                due_date = date(today.year, today.month, 28)

            if due_date < today:
                days_overdue = (today - due_date).days
                alerts.append({
                    "debt_id": debt["id"],
                    "debt_name": debt["name"],
                    "type": "overdue",
                    "severity": "critical",
                    "message": f"'{debt['name']}' venció hace {days_overdue} día(s). Paga lo que debes.",
                    "due_date": due_date.isoformat(),
                    "days_overdue": days_overdue,
                    "min_payment": debt.get("minimum_payment", 0),
                })
            elif due_date == today:
                alerts.append({
                    "debt_id": debt["id"],
                    "debt_name": debt["name"],
                    "type": "due_today",
                    "severity": "warning",
                    "message": f"'{debt['name']}' vence hoy. Pago mínimo: ${debt.get('minimum_payment', 0):,.0f}",
                    "due_date": due_date.isoformat(),
                    "days_overdue": 0,
                    "min_payment": debt.get("minimum_payment", 0),
                })
            elif (due_date - today).days <= 3:
                days_until = (due_date - today).days
                alerts.append({
                    "debt_id": debt["id"],
                    "debt_name": debt["name"],
                    "type": "upcoming",
                    "severity": "info",
                    "message": f"'{debt['name']}' vence en {days_until} día(s). Pago mínimo: ${debt.get('minimum_payment', 0):,.0f}",
                    "due_date": due_date.isoformat(),
                    "days_overdue": 0,
                    "min_payment": debt.get("minimum_payment", 0),
                })

        return sorted(alerts, key=lambda a: (-a["days_overdue"], a["due_date"]))
