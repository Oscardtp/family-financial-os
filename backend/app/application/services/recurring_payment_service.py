import logging
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.next_due_service import NextDueDateService
from app.application.services.transaction_service import TransactionService
from app.infrastructure.repositories.recurring_payment_repository import SQLAlchemyRecurringPaymentRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.datetime_utils import utc_now_naive

logger = logging.getLogger(__name__)


class RecurringPaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SQLAlchemyRecurringPaymentRepository(db)
        self.tx_repo = SQLAlchemyTransactionRepository(db)
        self.acc_repo = SQLAlchemyAccountRepository(db)

    async def list(self, household_id: str, skip: int = 0, limit: int = 100):
        return await self.repo.get_all(household_id, skip, limit)

    async def get(self, payment_id: str, household_id: str) -> dict:
        payment = await self.repo.get_by_id(payment_id)
        if not payment or payment["household_id"] != household_id:
            raise ValueError("Pago recurrente no encontrado")
        return payment

    async def create(self, data, household_id: str, user_id: str) -> dict:
        payload = {
            "household_id": household_id,
            **data.model_dump(),
        }
        if not payload.get("account_id"):
            accounts = await self.acc_repo.get_all(household_id, limit=1)
            if not accounts:
                raise ValueError("Necesitas tener una cuenta creada para registrar un pago recurrente.")
            payload["account_id"] = accounts[0]["id"]
        NextDueDateService.ensure_initial(payload)
        return await self.repo.create(payload)

    async def update(self, payment_id: str, data, household_id: str) -> dict:
        payment = await self.get(payment_id, household_id)
        update_data = data.model_dump(exclude_unset=True)
        if "amount" in update_data:
            update_data["amount"] = update_data["amount"]
        return await self.repo.update({**payment, **update_data})

    async def delete(self, payment_id: str, household_id: str):
        payment = await self.get(payment_id, household_id)
        await self.repo.delete(payment_id)

    async def pay(self, payment_id: str, user: dict) -> dict:
        payment = await self.get(payment_id, user["household_id"])
        await self._execute_payment(payment, user["id"])
        return await NextDueDateService.persist_mirror(self.repo, payment)

    async def process_due(self, household_id: str, user_id: str) -> dict:
        today = date.today()
        due_payments = await self.repo.get_due_today(household_id, today)

        processed = 0
        for payment in due_payments:
            try:
                charged = await self._execute_payment(payment, user_id)
                await NextDueDateService.persist_mirror(self.repo, payment, today)
                if charged:
                    processed += 1
            except Exception:
                continue

        return {"processed": processed}

    async def _execute_payment(self, payment: dict, user_id: str) -> bool:
        """Cobra un ciclo del pago recurrente. Devuelve True si movió dinero.

        D-4 (6.4A): un mismo ciclo sólo puede producir una Transaction, sin
        importar por qué ruta se cobre (directa, evento o process-due).

        Identidad del ciclo — ya existente en el dominio, no es una clave nueva:
        FinancialEvent con clave (household_id, source, source_id=obligation.id,
        due_date), alcanzable desde RecurringPayment vía
        Obligation.source_id == RecurringPayment.id
        (`SQLAlchemyFinancialEventRepository.get_pending_for_recurring`, la misma
        consulta que expone `GET /recurring-payments/{id}/pending-event`).

        D-5 (6.4C-C2a-2): esta clase resuelve CONTEXTO y reglas de dominio
        (idempotencia, cierre de ciclo); la mutación persistente de dinero
        vive únicamente en `TransactionService`.
        """
        today = date.today()

        # Guarda 1 — idempotencia por fuente y día: si esta fuente ya movió
        # dinero hoy por cualquier ruta, no se cobra de nuevo (tratado como
        # "ya pagado", sin error y sin `except: pass`).
        if await self.tx_repo.exists_for_recurring_on(payment["id"], today):
            logger.info(
                "D-4: pago recurrente %s ya cobrado hoy; se omite el duplicado",
                payment["id"],
            )
            return False

        # Guarda 2 — el ciclo vivo: mismo evento que ve el calendario.
        event_repo = SQLAlchemyFinancialEventRepository(self.db)
        cycle_event = await event_repo.get_pending_for_recurring(
            payment["household_id"], payment["id"]
        )

        # Autoridad monetaria única (D-5): valida fondos, crea la Transaction,
        # mueve Account.balance y escribe account_balance_history.
        await TransactionService(self.db).execute_payment(
            account_id=payment["account_id"],
            amount=payment["amount"],
            tx_type=payment["type"],
            tx_date=today,
            description=payment["name"],
            category_id=payment.get("category_id"),
            user_id=user_id,
            household_id=payment["household_id"],
            recurring_payment_id=payment["id"],
        )

        # Cierra el ciclo en el calendario: sin esto el evento sigue "pending"
        # y `POST /events/{id}/pay` vuelve a cobrar el mismo ciclo (D-4).
        # Sólo se cierra el estado; la Transaction ya existe, no se crea otra
        # (a diferencia de FinancialEventService.mark_as_paid).
        if cycle_event:
            await event_repo.mark_as_paid(
                cycle_event["id"],
                user_id,
                Decimal(str(payment["amount"])),
                utc_now_naive(),
            )

        return True
