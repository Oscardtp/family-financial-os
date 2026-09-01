from datetime import date
from decimal import Decimal

from app.infrastructure.repositories.obligation_repository import SQLAlchemyFinancialObligationRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.application.services.obligation_service import generate_events_for_obligation


class ObligationSyncService:
    def __init__(self, db):
        self.db = db
        self.obligation_repo = SQLAlchemyFinancialObligationRepository(db)
        self.event_repo = SQLAlchemyFinancialEventRepository(db)

    async def sync_debt(self, debt: dict, household_id: str):
        obligation = await self.obligation_repo.get_by_source(
            household_id, "SYSTEM", str(debt["id"])
        )
        obligation_data = {
            "household_id": household_id,
            "source": "SYSTEM",
            "source_id": str(debt["id"]),
            "name": debt["name"],
            "type": "debt",
            "amount": Decimal(str(debt.get("minimum_payment") or 0)),
            "currency": "COP",
            "frequency": "monthly",
            "anchor_day": debt.get("due_day") or 1,
            "recommended_offset_days": 5,
            "cutoff_offset_days": None,
            "reminder_days_before": 3,
            "is_active": debt.get("status") == "active",
            "confidence": 100,
        }
        if obligation:
            await self.obligation_repo.update({**obligation, **obligation_data})
            obligation_id = obligation["id"]
        else:
            created = await self.obligation_repo.create(obligation_data)
            obligation_id = created["id"]

        await self.event_repo.delete_upcoming_by_obligation(household_id, obligation_id, date.today())
        obligation_full = await self.obligation_repo.get_by_id(obligation_id)
        if obligation_full and obligation_full.get("amount") and obligation_full["amount"] > 0:
            await generate_events_for_obligation(self.event_repo, obligation_full, 12)

    async def sync_recurring(self, recurring: dict, household_id: str):
        obligation = await self.obligation_repo.get_by_source(
            household_id, "SYSTEM", str(recurring["id"])
        )
        obligation_data = {
            "household_id": household_id,
            "source": "SYSTEM",
            "source_id": str(recurring["id"]),
            "name": recurring["name"],
            "type": recurring["type"],
            "amount": Decimal(str(recurring["amount"])),
            "currency": "COP",
            "frequency": recurring["frequency"],
            "anchor_day": recurring.get("day_of_month") or 1,
            "recommended_offset_days": 5,
            "cutoff_offset_days": None,
            "reminder_days_before": 3,
            "account_id": str(recurring["account_id"]) if recurring.get("account_id") else None,
            "category_id": str(recurring["category_id"]) if recurring.get("category_id") else None,
            "is_active": recurring.get("is_active", True),
            "confidence": 100,
        }
        if obligation:
            await self.obligation_repo.update({**obligation, **obligation_data})
            obligation_id = obligation["id"]
        else:
            created = await self.obligation_repo.create(obligation_data)
            obligation_id = created["id"]

        await self.event_repo.delete_upcoming_by_obligation(household_id, obligation_id, date.today())
        obligation_full = await self.obligation_repo.get_by_id(obligation_id)
        if obligation_full and obligation_full.get("amount") and obligation_full["amount"] > 0:
            await generate_events_for_obligation(self.event_repo, obligation_full, 12)

    async def remove_for_source(self, household_id: str, source_id: str):
        obligation = await self.obligation_repo.get_by_source(household_id, "SYSTEM", source_id)
        if not obligation:
            return
        await self.event_repo.delete_upcoming_by_obligation(
            household_id, obligation["id"], date.today()
        )
        await self.obligation_repo.delete(obligation["id"])
