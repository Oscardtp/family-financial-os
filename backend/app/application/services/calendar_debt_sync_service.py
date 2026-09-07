import logging
from datetime import date
from decimal import Decimal

from app.infrastructure.repositories.obligation_repository import SQLAlchemyFinancialObligationRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.repositories.debt_repository import SQLAlchemyDebtRepository
from app.infrastructure.repositories.debt_payment_repository import SQLAlchemyDebtPaymentRepository
from app.infrastructure.repositories.debt_payment_override_repository import SQLAlchemyDebtPaymentOverrideRepository
from app.domain.value_objects.interest_rate import InterestRate, RateType
from app.financial_engine.rate_engine import RateEngine

logger = logging.getLogger(__name__)


class CalendarDebtSyncService:
    def __init__(self, db):
        self.db = db
        self.obligation_repo = SQLAlchemyFinancialObligationRepository(db)
        self.event_repo = SQLAlchemyFinancialEventRepository(db)
        self.debt_repo = SQLAlchemyDebtRepository(db)
        self.payment_repo = SQLAlchemyDebtPaymentRepository(db)
        self.override_repo = SQLAlchemyDebtPaymentOverrideRepository(db)

    async def on_event_paid(self, event: dict, household_id: str, user_id: str) -> dict | None:
        """Calendar event paid → create debt payment if linked to a debt."""
        obligation_id = event.get("obligation_id")
        if not obligation_id:
            return None

        obligation = await self.obligation_repo.get_by_id(obligation_id)
        if not obligation or obligation.get("source") != "SYSTEM":
            return None

        debt_id = obligation["source_id"]
        debt = await self.debt_repo.get_by_id(debt_id)
        if not debt or debt["household_id"] != household_id:
            return None
        if debt.get("status") == "paid_off":
            logger.info(
                "Calendar->Debt sync: skipping paid_off debt=%s for event=%s",
                debt_id, event["id"]
            )
            return None

        due = event.get("due_date")
        due_date = due if hasattr(due, "day") else date.fromisoformat(str(due))

        existing_payment = await self.payment_repo.find_by_debt_and_month(
            debt_id, due_date.year, due_date.month
        )
        if existing_payment and not existing_payment.get("is_reversed"):
            logger.info(
                "Calendar->Debt sync: payment already exists for debt=%s month=%s/%s",
                debt_id, due_date.year, due_date.month
            )
            return existing_payment

        payment_amount = Decimal(str(event.get("amount", 0)))
        if payment_amount <= 0:
            return None

        rate_type = debt.get("interest_rate_type") or "EA"
        try:
            rt = RateType(rate_type)
        except ValueError:
            rt = RateType.EA
        monthly_rate = RateEngine.to_monthly_rate(InterestRate(Decimal(str(debt["interest_rate"])), rt))
        interest_charge = (Decimal(str(debt["current_balance"])) * monthly_rate).quantize(Decimal("0.01"))
        principal_portion = payment_amount - interest_charge if payment_amount > interest_charge else Decimal("0")

        payment = await self.payment_repo.create({
            "debt_id": debt_id,
            "amount": payment_amount,
            "principal": principal_portion,
            "interest": min(payment_amount, interest_charge),
            "payment_date": due_date,
        })

        new_balance = max(Decimal("0"), Decimal(str(debt["current_balance"])) - principal_portion)
        new_status = "paid_off" if new_balance == 0 else debt["status"]
        await self.debt_repo.update({**debt, "current_balance": new_balance, "status": new_status})

        return payment

    async def on_event_unpaid(self, event: dict, household_id: str) -> int | None:
        """Calendar event unpaid → reverse debt payment if linked."""
        obligation_id = event.get("obligation_id")
        if not obligation_id:
            return None

        obligation = await self.obligation_repo.get_by_id(obligation_id)
        if not obligation or obligation.get("source") != "SYSTEM":
            return None

        debt_id = obligation["source_id"]
        debt = await self.debt_repo.get_by_id(debt_id)
        if not debt or debt["household_id"] != household_id:
            return None

        due = event.get("due_date")
        due_date = due if hasattr(due, "day") else date.fromisoformat(str(due))

        payment = await self.payment_repo.find_by_debt_and_month(
            debt_id, due_date.year, due_date.month
        )
        if not payment or payment.get("is_reversed"):
            return None

        new_balance = Decimal(str(debt["current_balance"])) + Decimal(str(payment["amount"]))
        new_status = "active" if debt["status"] == "paid_off" else debt["status"]
        await self.debt_repo.update({**debt, "current_balance": new_balance, "status": new_status})

        await self.payment_repo.reverse(payment["id"])

        return payment["id"]

    async def on_debt_payment(self, debt_id: str, payment_date: date, amount: Decimal, household_id: str) -> dict | None:
        """Debt payment created → mark corresponding calendar event as paid."""
        event = await self._find_event_for_debt(debt_id, payment_date, household_id)
        if not event:
            logger.warning(
                "Debt payment sync: no calendar event found for debt=%s month=%s/%s household=%s",
                debt_id, payment_date.year if hasattr(payment_date, 'year') else '?',
                payment_date.month if hasattr(payment_date, 'month') else '?',
                household_id
            )
            return None
        if event["status"] == "paid":
            logger.info(
                "Debt payment sync: calendar event already paid event=%s debt=%s",
                event["id"], debt_id
            )
            return event

        updated = await self.event_repo.mark_as_paid(
            event["id"],
            None,
            float(amount),
            payment_date,
        )
        logger.info(
            "Debt payment sync: marked calendar event as paid event=%s debt=%s amount=%s",
            event["id"], debt_id, amount
        )
        return updated

    async def on_debt_payment_reversed(self, debt_id: str, payment_date: date, household_id: str) -> dict | None:
        """Debt payment reversed → unpay corresponding calendar event."""
        event = await self._find_event_for_debt(debt_id, payment_date, household_id)
        if not event or event["status"] != "paid":
            return None

        event["status"] = "pending"
        event["paid_at"] = None
        event["paid_amount"] = None
        event["paid_by"] = None
        return await self.event_repo.update(event)

    async def on_debt_month_marked_paid(self, debt_id: str, year: int, month: int, household_id: str) -> dict | None:
        """Debt month marked as paid (override) → mark calendar event as paid."""
        due_date = date(year, month, 1)
        event = await self._find_event_for_debt(debt_id, due_date, household_id)
        if not event or event["status"] == "paid":
            return event

        from decimal import Decimal as D
        updated = await self.event_repo.mark_as_paid(
            event["id"],
            None,
            float(D(str(event.get("amount", 0)))),
            due_date,
        )
        return updated

    async def _find_event_for_debt(self, debt_id: str, reference_date: date, household_id: str) -> dict | None:
        """Find the pending calendar event for a debt in a specific month."""
        obligation = await self.obligation_repo.get_by_source(
            household_id, "SYSTEM", debt_id
        )
        if not obligation:
            logger.warning(
                "Debt sync: no obligation found for debt=%s household=%s",
                debt_id, household_id
            )
            return None

        year, month = reference_date.year, reference_date.month
        if month == 12:
            date_from = date(year, 12, 1)
            date_to = date(year + 1, 1, 1)
        else:
            date_from = date(year, month, 1)
            date_to = date(year, month + 1, 1)

        events = await self.event_repo.get_by_date_range(household_id, date_from, date_to)
        for e in events:
            if e.get("obligation_id") == obligation["id"] and e.get("status") == "pending":
                return e

        logger.warning(
            "Debt sync: no pending event found for obligation=%s month=%s/%s (events in month: %d)",
            obligation["id"], year, month, len(events)
        )
        return None
