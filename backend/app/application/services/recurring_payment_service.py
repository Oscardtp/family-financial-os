from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.recurring_payment_repository import SQLAlchemyRecurringPaymentRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository


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
        if not payload.get("next_due_date"):
            payload["next_due_date"] = self._calculate_next_due(
                payload.get("frequency", "monthly"),
                payload.get("day_of_month", 1),
                date.today(),
            )
        return await self.repo.create(payload)

    async def update(self, payment_id: str, data, household_id: str) -> dict:
        payment = await self.get(payment_id, household_id)
        update_data = data.model_dump(exclude_unset=True)
        if "amount" in update_data:
            update_data["amount"] = float(update_data["amount"])
        return await self.repo.update({**payment, **update_data})

    async def delete(self, payment_id: str, household_id: str):
        payment = await self.get(payment_id, household_id)
        await self.repo.delete(payment_id)

    async def pay(self, payment_id: str, user: dict) -> dict:
        payment = await self.get(payment_id, user["household_id"])
        await self._execute_payment(payment, user["id"])
        next_due = self._calculate_next_due(
            payment["frequency"], payment["day_of_month"], date.today()
        )
        return await self.repo.update({**payment, "next_due_date": next_due})

    async def process_due(self, household_id: str, user_id: str) -> dict:
        today = date.today()
        due_payments = await self.repo.get_due_today(household_id, today)

        processed = 0
        for payment in due_payments:
            try:
                await self._execute_payment(payment, user_id)
                next_due = self._calculate_next_due(
                    payment["frequency"], payment["day_of_month"], today
                )
                await self.repo.update({**payment, "next_due_date": next_due})
                processed += 1
            except Exception:
                continue

        return {"processed": processed}

    async def _execute_payment(self, payment: dict, user_id: str):
        account = await self.acc_repo.get_by_id(payment["account_id"])
        if not account:
            raise ValueError("Cuenta no encontrada")

        if payment["type"] == "expense" and account["type"] != "credit_card":
            if account["balance"] < Decimal(str(payment["amount"])):
                raise ValueError(
                    f"No tienes suficiente plata. Disponible: ${account['balance']:,.2f}, "
                    f"necesitas: ${Decimal(str(payment['amount'])):,.2f}"
                )

        today = date.today()
        await self.tx_repo.create({
            "account_id": payment["account_id"],
            "category_id": payment.get("category_id"),
            "user_id": user_id,
            "type": payment["type"],
            "amount": payment["amount"],
            "description": payment["name"],
            "date": today,
        })

        amount = Decimal(str(payment["amount"]))
        if payment["type"] == "income":
            await self.acc_repo.update_balance(account["id"], amount)
        elif payment["type"] == "expense":
            deducted = await self.acc_repo.deduct_balance(account["id"], amount)
            if not deducted:
                raise ValueError("No tienes suficiente plata para este pago")
        else:
            await self.acc_repo.update_balance(account["id"], amount)

    @staticmethod
    def _calculate_next_due(frequency: str, day_of_month: int, from_date: date) -> date:
        if frequency == "weekly":
            return from_date + timedelta(weeks=1)
        elif frequency == "biweekly":
            return from_date + timedelta(weeks=2)
        elif frequency == "monthly":
            next_month = from_date.month + 1
            next_year = from_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            try:
                return date(next_year, next_month, min(day_of_month, 28))
            except ValueError:
                return date(next_year, next_month, 28)
        elif frequency == "yearly":
            try:
                return date(from_date.year + 1, from_date.month, min(day_of_month, 28))
            except ValueError:
                return date(from_date.year + 1, from_date.month, 28)
        return from_date + timedelta(days=30)
