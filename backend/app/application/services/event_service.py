import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import uuid

from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.repositories.notification_repository import SQLAlchemyNotificationRepository

logger = logging.getLogger(__name__)


class FinancialEventService:
    def __init__(self, db):
        self.db = db
        self.repo = SQLAlchemyFinancialEventRepository(db)
        self.notification_repo = SQLAlchemyNotificationRepository(db)

    async def get_month(self, household_id: str, year: int, month: int) -> list[dict]:
        if month == 12:
            date_from = date(year, 12, 1)
            date_to = date(year + 1, 1, 1)
        else:
            date_from = date(year, month, 1)
            date_to = date(year, month + 1, 1)
        return await self.repo.get_by_date_range(household_id, date_from, date_to)

    async def get_range(self, household_id: str, date_from: date, date_to: date) -> list[dict]:
        return await self.repo.get_by_date_range(household_id, date_from, date_to)

    async def get_upcoming(self, household_id: str, days: int = 30) -> list[dict]:
        return await self.repo.get_upcoming(household_id, date.today(), days)

    async def get(self, event_id: str, household_id: str) -> dict:
        event = await self.repo.get_by_id(event_id)
        if not event or event["household_id"] != household_id:
            raise ValueError("No encontramos este evento")
        return event

    async def create(self, data, household_id: str, user_id: str) -> dict:
        return await self.repo.create({
            "household_id": household_id,
            "source": "USER",
            "source_id": None,
            "type": data.type,
            "title": data.title,
            "amount": Decimal(str(data.amount)),
            "currency": data.currency,
            "due_date": data.due_date,
            "recommended_date": data.recommended_date,
            "cutoff_date": data.cutoff_date,
            "status": "pending",
            "account_id": str(data.account_id) if data.account_id else None,
            "responsible_member_id": str(data.responsible_member_id) if data.responsible_member_id else None,
            "is_recurrent": False,
            "reminder_days_before": data.reminder_days_before,
            "notes": data.notes,
            "confirmed": True,
            "visibility": data.visibility,
            "confidence": data.confidence,
            "payment_method": data.payment_method,
            "consequence_note": data.consequence_note,
            "category_id": str(data.category_id) if data.category_id else None,
        })

    async def update(self, event_id: str, data, household_id: str) -> dict:
        event = await self.get(event_id, household_id)
        update_data = data.model_dump(exclude_unset=True)
        if "amount" in update_data:
            update_data["amount"] = Decimal(str(update_data["amount"]))
        if update_data.get("notes") == "":
            update_data["notes"] = None
        for key in ("account_id", "responsible_member_id"):
            if key in update_data and update_data[key] is not None:
                update_data[key] = str(update_data[key])
        return await self.repo.update({**event, **update_data})

    async def delete(self, event_id: str, household_id: str):
        event = await self.get(event_id, household_id)
        await self.repo.delete(event_id)

    async def mark_as_paid(self, event_id: str, user: dict) -> dict:
        event = await self.get(event_id, user["household_id"])
        if event["status"] == "paid":
            return event
        updated = await self.repo.mark_as_paid(
            event_id,
            user["id"],
            Decimal(str(event["amount"])),
            datetime.now(timezone.utc),
        )
        await self._notify_family_payment(updated, user)

        from app.application.services.calendar_debt_sync_service import CalendarDebtSyncService
        sync = CalendarDebtSyncService(self.db)
        await sync.on_event_paid(event, user["household_id"], user["id"])

        return updated

    async def unpay(self, event_id: str, user: dict) -> dict:
        event = await self.get(event_id, user["household_id"])
        logger.info("Anulando pago del evento %s (%s)", event["id"], event["title"])
        event["status"] = "pending"
        event["paid_at"] = None
        event["paid_amount"] = None
        event["paid_by"] = None

        from app.application.services.calendar_debt_sync_service import CalendarDebtSyncService
        sync = CalendarDebtSyncService(self.db)
        await sync.on_event_unpaid(event, user["household_id"])

        from app.presentation.audit_helper import log_action
        await log_action(
            self.db,
            household_id=user["household_id"],
            user_id=user["id"],
            user_email=user.get("email", ""),
            action="event_unpaid",
            entity_type="financial_event",
            entity_id=event["id"],
            entity_name=event["title"],
            details=f"Monto: ${Decimal(str(event['amount'])):,.0f}",
        )

        result = await self.repo.update(event)
        logger.info("Pago anulado exitosamente para evento %s", event["id"])
        return result

    async def _notify_family_payment(self, event: dict, user: dict):
        member_name = user.get("name") or "Alguien"
        title = f"{event['title']} ya está pagado"
        message = (
            f"{member_name} registró el pago de {event['title']} "
            f"por ${Decimal(str(event['amount'])):,.0f}."
        )
        await self.notification_repo.notify_household_members(
            household_id=user["household_id"],
            exclude_user_id=user["id"],
            title=title,
            message=message,
            data={"event_id": event["id"], "action": "event_paid"},
        )
