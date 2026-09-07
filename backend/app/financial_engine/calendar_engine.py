from datetime import date, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
import uuid


@dataclass
class GeneratedEvent:
    source: str
    source_id: str
    type: str
    title: str
    amount: Decimal
    due_date: date
    recommended_date: date = None
    cutoff_date: date = None
    account_id: str = None
    is_recurrent: bool = False
    recurrence_group_id: str = None
    confirmed: bool = True


class CalendarEngine:

    @staticmethod
    def _calculate_recommended_date(due_date: date, days_before: int = 5) -> date:
        recommended = due_date - timedelta(days=days_before)
        return recommended if recommended >= date.today() else due_date

    @staticmethod
    def _next_month_day(day_of_month: int, reference: date) -> date:
        year = reference.year
        month = reference.month + 1
        if month > 12:
            month = 1
            year += 1
        max_day = CalendarEngine._days_in_month(year, month)
        return date(year, month, min(day_of_month, max_day))

    @staticmethod
    def _next_week_day(reference: date) -> date:
        return reference + timedelta(days=7)

    @staticmethod
    def _next_biweekly_day(reference: date) -> date:
        return reference + timedelta(days=14)

    @staticmethod
    def _next_year_day(day_of_month: int, reference: date) -> date:
        year = reference.year + 1
        max_day = CalendarEngine._days_in_month(year, reference.month)
        return date(year, reference.month, min(day_of_month, max_day))

    @staticmethod
    def _days_in_month(year: int, month: int) -> int:
        if month == 12:
            return (date(year + 1, 1, 1) - date(year, 12, 1)).days
        return (date(year, month + 1, 1) - date(year, month, 1)).days

    def generate_events_from_debt(self, debt: dict, months_ahead: int = 6) -> list[GeneratedEvent]:
        events = []
        due_day = debt.get("due_day", 1)
        today = date.today()
        start_date = today.replace(day=1)
        end_date = date(today.year + (today.month + months_ahead) // 12,
                        ((today.month + months_ahead - 1) % 12) + 1, 1)

        current = start_date
        while current <= end_date:
            max_day = self._days_in_month(current.year, current.month)
            due = date(current.year, current.month, min(due_day, max_day))

            if due >= today:
                recommended = self._calculate_recommended_date(due, 5)
                events.append(GeneratedEvent(
                    source="debt",
                    source_id=str(debt["id"]),
                    type="payment",
                    title=debt["name"],
                    amount=Decimal(str(debt.get("minimum_payment", 0))),
                    due_date=due,
                    recommended_date=recommended,
                    cutoff_date=due,
                    account_id=debt.get("account_id"),
                    is_recurrent=True,
                    recurrence_group_id=str(debt["id"]),
                    confirmed=True,
                ))
            current = self._next_month_day(1, current)

        return events

    def generate_events_from_recurring(self, recurring: dict, months_ahead: int = 6) -> list[GeneratedEvent]:
        events = []
        if not recurring.get("is_active", True):
            return events

        frequency = recurring.get("frequency", "monthly")
        day_of_month = recurring.get("day_of_month", 1)
        next_due = recurring.get("next_due_date")
        if isinstance(next_due, str):
            next_due = date.fromisoformat(next_due)

        today = date.today()
        count = 0
        current = next_due

        while count < months_ahead:
            if current >= today:
                recommended = self._calculate_recommended_date(current, 5)
                event_type = recurring.get("type", "expense")
                events.append(GeneratedEvent(
                    source="recurring",
                    source_id=str(recurring["id"]),
                    type="income" if event_type == "income" else "payment",
                    title=recurring["name"],
                    amount=Decimal(str(recurring["amount"])),
                    due_date=current,
                    recommended_date=recommended,
                    cutoff_date=current,
                    account_id=recurring.get("account_id"),
                    is_recurrent=True,
                    recurrence_group_id=str(recurring["id"]),
                    confirmed=True,
                ))

            if frequency == "monthly":
                current = self._next_month_day(day_of_month, current)
            elif frequency == "weekly":
                current = self._next_week_day(current)
            elif frequency == "biweekly":
                current = self._next_biweekly_day(current)
            elif frequency == "yearly":
                current = self._next_year_day(day_of_month, current)
            else:
                break

            count += 1

        return events

    def detect_pattern(self, events: list[dict]) -> dict | None:
        if len(events) < 3:
            return None

        amounts = [e["amount"] for e in events]
        days = [e["due_date"].day if isinstance(e["due_date"], date) else date.fromisoformat(str(e["due_date"])).day
                for e in events]

        avg_amount = sum(amounts) / len(amounts)
        avg_day = sum(days) / len(days)
        amounts_close = all(abs(a - avg_amount) / avg_amount < Decimal("0.15") for a in amounts) if avg_amount > 0 else False
        days_close = all(abs(d - avg_day) <= 3 for d in days)

        if amounts_close and days_close:
            return {
                "title": events[0]["title"],
                "avg_amount": round(avg_amount, 2),
                "avg_day": round(avg_day),
                "occurrences": len(events),
                "source": events[0].get("source", "manual"),
                "source_id": events[0].get("source_id"),
            }
        return None

    def calculate_status(self, due_date: date, today: date = None) -> str:
        if today is None:
            today = date.today()
        if due_date < today:
            return "overdue"
        delta = (due_date - today).days
        if delta <= 3:
            return "upcoming"
        return "pending"
