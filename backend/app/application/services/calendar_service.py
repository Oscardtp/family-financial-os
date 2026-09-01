from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.infrastructure.repositories.debt_repository import SQLAlchemyDebtRepository
from app.infrastructure.repositories.recurring_payment_repository import SQLAlchemyRecurringPaymentRepository
from app.financial_engine.calendar_engine import CalendarEngine


class CalendarService:
    def __init__(
        self,
        db,
        account_repo=None,
        event_repo=None,
        budget_repo=None,
        tx_repo=None,
    ):
        self.db = db
        self.account_repo = account_repo or SQLAlchemyAccountRepository(db)
        self.event_repo = event_repo or SQLAlchemyFinancialEventRepository(db)
        self.budget_repo = budget_repo or SQLAlchemyBudgetRepository(db)
        self.tx_repo = tx_repo
        self.debt_repo = SQLAlchemyDebtRepository(db)
        self.recurring_repo = SQLAlchemyRecurringPaymentRepository(db)
        self.engine = CalendarEngine()

    async def availability(self, household_id: str, days: int = 7) -> dict:
        today = date.today()
        date_to = today + timedelta(days=days)

        accounts = await self.account_repo.get_all(household_id)
        available = sum(
            Decimal(str(a["balance"])) for a in accounts if a.get("type") != "credit_card"
        )

        events = await self.event_repo.get_by_date_range(household_id, today, date_to)

        upcoming_payments = Decimal("0")
        expected_income = Decimal("0")
        expected_expenses = Decimal("0")
        cash_account_ids = {
            str(a["id"]) for a in accounts if a.get("type") == "cash"
        }
        cash_balance = sum(
            Decimal(str(a["balance"])) for a in accounts if a.get("type") == "cash"
        )
        cash_expenses = Decimal("0")

        for e in events:
            if e.get("status") == "paid":
                continue
            amount = Decimal(str(e["amount"]))
            if e.get("type") == "income":
                expected_income += amount
            else:
                upcoming_payments += amount
                expected_expenses += amount
                if e.get("account_id") and str(e["account_id"]) in cash_account_ids:
                    cash_expenses += amount

        cash_needed = max(cash_expenses - cash_balance, Decimal("0"))

        budget_committed = await self._get_budget_committed(household_id, today, date_to)

        return {
            "days": days,
            "available": float(available),
            "upcoming_payments": float(upcoming_payments),
            "projected_available": float(available - upcoming_payments),
            "cash_needed": float(cash_needed),
            "expected_income": float(expected_income),
            "expected_expenses": float(expected_expenses),
            "budget_committed": float(budget_committed),
        }

    async def _get_budget_committed(self, household_id: str, date_from: date, date_to: date) -> Decimal:
        if not self.tx_repo:
            return Decimal("0")
        today = date.today()
        budgets = await self.budget_repo.get_all(household_id, today.month, today.year)
        if not budgets:
            return Decimal("0")

        spending = await self.tx_repo.get_totals_by_category(
            household_id,
            date_from=date_from,
            date_to=date_to,
        )
        spending_by_category = {str(s["category_id"]): Decimal(str(s["total"])) for s in spending}

        total = Decimal("0")
        for b in budgets:
            cat_id = str(b.get("category_id"))
            if cat_id in spending_by_category:
                total += spending_by_category[cat_id]
        return total

    async def prepare_month(self, household_id: str) -> dict:
        today = date.today()
        year, month = today.year, today.month

        if month == 12:
            date_from = date(year, 12, 1)
            date_to = date(year + 1, 1, 1)
        else:
            date_from = date(year, month, 1)
            date_to = date(year, month + 1, 1)

        events = await self.event_repo.get_by_date_range(household_id, date_from, date_to)

        scheduled_payments = [e for e in events if e.get("type") in ("expense", "payment", "debt") and e.get("status") != "paid"]
        expected_income = [e for e in events if e.get("type") == "income" and e.get("status") != "paid"]

        debts = await self.debt_repo.get_all(household_id)
        new_debts = [d for d in debts if d.get("status") == "active"]

        recurring = await self.recurring_repo.get_active(household_id)

        return {
            "month": f"{year}-{month:02d}",
            "scheduled_payments_count": len(scheduled_payments),
            "scheduled_payments_amount": float(sum(Decimal(str(e["amount"])) for e in scheduled_payments)),
            "expected_income": float(sum(Decimal(str(e["amount"])) for e in expected_income)),
            "new_debts_count": len(new_debts),
            "new_recurring_count": len(recurring),
        }

    async def sync_events(self, household_id: str) -> dict:
        debts = await self.debt_repo.get_all(household_id)
        active_debts = [d for d in debts if d.get("status") == "active"]
        recurring = await self.recurring_repo.get_active(household_id)

        created = 0
        skipped = 0

        for debt in active_debts:
            events = self.engine.generate_events_from_debt(debt, months_ahead=6)
            for ev in events:
                exists = await self.event_repo.exists_for_source(
                    household_id, ev.source, ev.source_id, ev.due_date
                )
                if not exists:
                    await self.event_repo.create({
                        "household_id": household_id,
                        "source": ev.source,
                        "source_id": ev.source_id,
                        "type": ev.type,
                        "title": ev.title,
                        "amount": ev.amount,
                        "due_date": ev.due_date,
                        "recommended_date": ev.recommended_date,
                        "cutoff_date": ev.cutoff_date,
                        "account_id": ev.account_id,
                        "is_recurrent": ev.is_recurrent,
                        "recurrence_group_id": ev.recurrence_group_id,
                        "confirmed": ev.confirmed,
                        "status": self.engine.calculate_status(ev.due_date),
                    })
                    created += 1
                else:
                    skipped += 1

        for rec in recurring:
            events = self.engine.generate_events_from_recurring(rec, months_ahead=6)
            for ev in events:
                exists = await self.event_repo.exists_for_source(
                    household_id, ev.source, ev.source_id, ev.due_date
                )
                if not exists:
                    await self.event_repo.create({
                        "household_id": household_id,
                        "source": ev.source,
                        "source_id": ev.source_id,
                        "type": ev.type,
                        "title": ev.title,
                        "amount": ev.amount,
                        "due_date": ev.due_date,
                        "recommended_date": ev.recommended_date,
                        "cutoff_date": ev.cutoff_date,
                        "account_id": ev.account_id,
                        "is_recurrent": ev.is_recurrent,
                        "recurrence_group_id": ev.recurrence_group_id,
                        "confirmed": ev.confirmed,
                        "status": self.engine.calculate_status(ev.due_date),
                    })
                    created += 1
                else:
                    skipped += 1

        return {"created": created, "skipped": skipped}
