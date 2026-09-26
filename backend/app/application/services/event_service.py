import logging
from datetime import date
from decimal import Decimal

from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.repositories.notification_repository import SQLAlchemyNotificationRepository
from app.infrastructure.repositories.recurring_payment_repository import SQLAlchemyRecurringPaymentRepository
from app.infrastructure.repositories.obligation_repository import SQLAlchemyFinancialObligationRepository
from app.application.services.next_due_service import NextDueDateService
from app.application.services.transaction_service import TransactionService
from app.infrastructure.datetime_utils import utc_now_naive

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

        # 1) Dinero primero, vía la única autoridad monetaria (D-5).
        #    Si el cobro falla, el evento queda intacto y nada persiste.
        await self._execute_payment_for_recurring_event(event, user)

        # 2) Sólo después de un cobro exitoso se cambia el estado de negocio.
        updated = await self.repo.mark_as_paid(
            event_id,
            user["id"],
            Decimal(str(event["amount"])),
            utc_now_naive(),
        )
        await self._notify_family_payment(updated, user)

        from app.application.services.calendar_debt_sync_service import CalendarDebtSyncService
        sync = CalendarDebtSyncService(self.db)
        await sync.on_event_paid(event, user["household_id"], user["id"])

        return updated

    async def _execute_payment_for_recurring_event(self, event: dict, user: dict) -> None:
        """Cobra desde el calendario un evento ligado a un RecurringPayment.

        Resuelve el contexto (obligación → pago recurrente → cuenta) y delega
        toda la mutación monetaria en `TransactionService` (D-5): valida fondos,
        crea la Transaction, actualiza Account.balance y registra
        account_balance_history. Los eventos de deuda no entran aquí (G-1 sigue
        fuera de alcance) y los eventos sin obligación tampoco.
        """
        if not event.get("obligation_id"):
            return

        obligation_repo = SQLAlchemyFinancialObligationRepository(self.db)
        obligation = await obligation_repo.get_by_id(event["obligation_id"])
        if not obligation:
            return

        if obligation["source"] != "SYSTEM" or not obligation.get("source_id"):
            return

        recurring_id = obligation["source_id"]
        rp_repo = SQLAlchemyRecurringPaymentRepository(self.db)
        recurring = await rp_repo.get_by_id(recurring_id)
        if not recurring:
            return

        account_id = event.get("account_id") or recurring.get("account_id")
        if not account_id:
            return

        await TransactionService(self.db).execute_payment(
            account_id=account_id,
            amount=event["amount"],
            tx_type=event["type"],
            tx_date=event["due_date"],
            description=event["title"],
            category_id=event.get("category_id"),
            user_id=user["id"],
            household_id=event["household_id"],
            recurring_payment_id=recurring_id,
        )

        await NextDueDateService.persist_mirror(rp_repo, recurring)

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
