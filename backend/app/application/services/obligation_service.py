from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
import uuid

from app.infrastructure.repositories.obligation_repository import SQLAlchemyFinancialObligationRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository


def _clamp_day(year: int, month: int, day: int) -> int:
    return min(day, monthrange(year, month)[1])


def _add_months_to(base: date, months: int) -> date:
    total = base.year * 12 + (base.month - 1) + months
    year, month = total // 12, total % 12 + 1
    return date(year, month, 1)


def _start_month(base: date, anchor_day: int | None) -> date:
    start = date(base.year, base.month, 1)
    if anchor_day is not None and anchor_day < base.day:
        start = _add_months_to(start, 1)
    return start


def _occurrence_dates(start: date, month_offset: int, anchor_day: int,
                      offset_recommended: int, offset_cutoff: int | None):
    year, month = start.year, start.month
    total = (year * 12 + (month - 1)) + month_offset
    year, month = total // 12, total % 12 + 1
    due = date(year, month, _clamp_day(year, month, anchor_day))
    recommended = due - timedelta(days=offset_recommended)
    cutoff = (due - timedelta(days=offset_cutoff)) if offset_cutoff is not None else None
    return due, recommended, cutoff


async def generate_events_for_obligation(event_repo, obligation: dict, months: int):
    anchor_day = obligation.get("anchor_day") or 1
    offset_recommended = obligation.get("recommended_offset_days") or 0
    offset_cutoff = obligation.get("cutoff_offset_days")
    visibility = "confirmed" if obligation["source"] == "USER" else "estimated"
    start = _start_month(date.today(), anchor_day)
    for i in range(months):
        due, recommended, cutoff = _occurrence_dates(
            start, i, anchor_day, offset_recommended, offset_cutoff
        )
        await event_repo.create({
            "household_id": obligation["household_id"],
            "source": obligation["source"],
            "source_id": obligation["id"],
            "type": obligation["type"],
            "title": obligation["name"],
            "amount": Decimal(str(obligation["amount"])),
            "currency": obligation["currency"],
            "due_date": due,
            "recommended_date": recommended,
            "cutoff_date": cutoff,
            "status": "pending",
            "account_id": obligation.get("account_id"),
            "responsible_member_id": obligation.get("responsible_member_id"),
            "is_recurrent": True,
            "recurrence_group_id": obligation["id"],
            "reminder_days_before": obligation.get("reminder_days_before", 3),
            "notes": obligation.get("notes"),
            "confirmed": True,
            "obligation_id": obligation["id"],
            "visibility": visibility,
            "confidence": obligation.get("confidence", 100),
        })


class FinancialObligationService:
    def __init__(self, db):
        self.db = db
        self.repo = SQLAlchemyFinancialObligationRepository(db)
        self.event_repo = SQLAlchemyFinancialEventRepository(db)

    async def list(self, household_id: str, skip: int = 0, limit: int = 100):
        return await self.repo.get_all(household_id, skip, limit)

    async def get(self, obligation_id: str, household_id: str) -> dict:
        obligation = await self.repo.get_by_id(obligation_id)
        if not obligation or obligation["household_id"] != household_id:
            raise ValueError("No encontramos esta obligación")
        return obligation

    async def create(self, data, household_id: str, user_id: str) -> dict:
        obligation = await self.repo.create({
            "household_id": household_id,
            "source": data.source,
            "source_id": str(data.source_id) if data.source_id else None,
            "name": data.name,
            "type": data.type,
            "amount": Decimal(str(data.amount)),
            "currency": data.currency,
            "frequency": data.frequency,
            "anchor_day": data.anchor_day,
            "recommended_offset_days": data.recommended_offset_days,
            "cutoff_offset_days": data.cutoff_offset_days,
            "reminder_days_before": data.reminder_days_before,
            "account_id": str(data.account_id) if data.account_id else None,
            "category_id": str(data.category_id) if data.category_id else None,
            "responsible_member_id": str(data.responsible_member_id) if data.responsible_member_id else None,
            "is_active": data.is_active,
            "confidence": data.confidence,
            "notes": data.notes,
        })
        await generate_events_for_obligation(self.event_repo, obligation, data.generate_months)
        return obligation

    async def update(self, obligation_id: str, data, household_id: str) -> dict:
        obligation = await self.get(obligation_id, household_id)
        update_data = data.model_dump(exclude_unset=True)
        if "amount" in update_data:
            update_data["amount"] = Decimal(str(update_data["amount"]))
        for key in ("source_id", "account_id", "category_id", "responsible_member_id"):
            if key in update_data and update_data[key] is not None:
                update_data[key] = str(update_data[key])
        return await self.repo.update({**obligation, **update_data})

    async def delete(self, obligation_id: str, household_id: str):
        obligation = await self.get(obligation_id, household_id)
        await self.repo.delete(obligation_id)
