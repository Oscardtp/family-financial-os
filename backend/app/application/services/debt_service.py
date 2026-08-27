from datetime import datetime
from decimal import Decimal
from calendar import month_name
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.debt_repository import SQLAlchemyDebtRepository
from app.infrastructure.repositories.debt_payment_repository import SQLAlchemyDebtPaymentRepository
from app.infrastructure.repositories.debt_payment_override_repository import SQLAlchemyDebtPaymentOverrideRepository
from app.financial_engine.amortization import AmortizationEngine
from app.domain.value_objects.money import Money


class DebtService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.debt_repo = SQLAlchemyDebtRepository(db)
        self.payment_repo = SQLAlchemyDebtPaymentRepository(db)
        self.override_repo = SQLAlchemyDebtPaymentOverrideRepository(db)

    async def list(self, household_id: str, skip: int = 0, limit: int = 100):
        return await self.debt_repo.get_all(household_id, skip, limit)

    async def get(self, debt_id: str, household_id: str) -> dict:
        debt = await self.debt_repo.get_by_id(debt_id)
        if not debt or debt["household_id"] != household_id:
            raise ValueError("Deuda no encontrada")
        return debt

    async def create(self, data, household_id: str) -> dict:
        return await self.debt_repo.create({
            "household_id": household_id,
            **data.model_dump(),
        })

    async def update(self, debt_id: str, data, household_id: str) -> dict:
        debt = await self.get(debt_id, household_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.debt_repo.update({**debt, **update_data})

    async def delete(self, debt_id: str, household_id: str):
        debt = await self.get(debt_id, household_id)
        await self.debt_repo.delete(debt_id)

    async def create_payment(self, debt_id: str, data, user: dict) -> dict:
        debt = await self.get(debt_id, user["household_id"])

        monthly_rate = Decimal(str(debt["interest_rate"])) / Decimal("1200")
        interest_charge = (Decimal(str(debt["current_balance"])) * monthly_rate).quantize(Decimal("0.01"))
        payment_amount = Decimal(str(data.amount))

        principal_portion = payment_amount - interest_charge if payment_amount > interest_charge else Decimal("0")

        payment = await self.payment_repo.create({
            "debt_id": debt_id,
            "amount": payment_amount,
            "principal": principal_portion,
            "interest": min(payment_amount, interest_charge),
            "payment_date": data.payment_date,
        })

        new_balance = max(Decimal("0"), Decimal(str(debt["current_balance"])) - principal_portion)
        new_status = "paid_off" if new_balance == 0 else debt["status"]
        await self.debt_repo.update({**debt, "current_balance": new_balance, "status": new_status})

        return payment

    async def reverse_payment(self, debt_id: str, payment_id: str, household_id: str):
        debt = await self.get(debt_id, household_id)

        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment or payment["debt_id"] != debt_id:
            raise ValueError("Pago no encontrado")
        if payment["is_reversed"]:
            raise ValueError("Este pago ya fue reversado")

        await self.payment_repo.reverse(payment_id)

        new_balance = debt["current_balance"] + payment["amount"]
        new_status = "active" if debt["status"] == "paid_off" else debt["status"]
        await self.debt_repo.update({**debt, "current_balance": new_balance, "status": new_status})

    async def toggle_status(self, debt_id: str, user: dict) -> dict:
        debt = await self.get(debt_id, user["household_id"])

        current_status = debt.get("status", "active")
        if current_status == "paid_off":
            raise ValueError("No se puede cambiar el estado de una deuda pagada")

        new_status = "paused" if current_status == "active" else "active"
        if new_status == "active" and debt["current_balance"] <= 0:
            raise ValueError("No se puede reactivar una deuda con saldo cero")

        return await self.debt_repo.update({**debt, "status": new_status})

    async def list_payments(self, debt_id: str, household_id: str, skip: int = 0, limit: int = 100):
        await self.get(debt_id, household_id)
        return await self.payment_repo.get_by_debt_id(debt_id, skip, limit)

    async def mark_month_paid(self, debt_id: str, data, user: dict):
        debt = await self.get(debt_id, user["household_id"])

        existing = await self.override_repo.get_by_debt_and_month(debt_id, data.year, data.month)
        if existing:
            raise ValueError("Este mes ya esta marcado como pagado")

        await self.override_repo.create({
            "debt_id": debt_id,
            "year": data.year,
            "month": data.month,
            "is_paid": True,
            "marked_by": user.get("id"),
        })

        min_payment = Decimal(str(debt.get("minimum_payment", 0)))
        if min_payment <= 0:
            min_payment = Decimal(str(debt["current_balance"])) * Decimal("0.1")
        new_balance = max(Decimal("0"), Decimal(str(debt["current_balance"])) - min_payment)
        new_status = "paid_off" if new_balance == 0 else debt["status"]
        await self.debt_repo.update({**debt, "current_balance": new_balance, "status": new_status})

        return {"status": "ok", "year": data.year, "month": data.month}

    async def get_payment_history(self, debt_id: str, household_id: str):
        from app.presentation.schemas.schemas import PaymentMonthHistory

        debt = await self.get(debt_id, household_id)

        payments = await self.payment_repo.get_by_debt_id(debt_id, limit=1000)
        overrides = await self.override_repo.get_by_debt_id(debt_id)

        today = datetime.now()
        start = debt.get("start_date")
        if start:
            if hasattr(start, 'year'):
                start_year, start_month = start.year, start.month
            else:
                start_year, start_month = today.year, today.month
        else:
            start_year, start_month = today.year, today.month

        paid_months = {}
        for p in [p for p in payments if not p.get("is_reversed")]:
            pd = p["payment_date"]
            key = (pd.year, pd.month) if hasattr(pd, 'year') else (today.year, today.month)
            if key not in paid_months:
                paid_months[key] = p

        override_months = {}
        for o in overrides:
            if o["is_paid"]:
                override_months[(o["year"], o["month"])] = o

        history = []
        current_year, current_month = start_year, start_month
        while (current_year < today.year) or (current_year == today.year and current_month <= today.month):
            key = (current_year, current_month)
            if key in paid_months:
                p = paid_months[key]
                history.append(PaymentMonthHistory(
                    year=current_year, month=current_month, status="paid",
                    payment_id=p["id"], amount=p["amount"],
                ))
            elif key in override_months:
                history.append(PaymentMonthHistory(
                    year=current_year, month=current_month, status="paid",
                    amount=Decimal(str(debt.get("minimum_payment", 0))),
                ))
            else:
                history.append(PaymentMonthHistory(
                    year=current_year, month=current_month, status="pending",
                ))
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        history.reverse()
        return history

    async def get_amortization(self, debt_id: str, household_id: str):
        debt = await self.get(debt_id, household_id)

        engine = AmortizationEngine()
        schedule = engine.generate_schedule(
            balance=debt["current_balance"],
            annual_rate=debt["interest_rate"],
            monthly_payment=debt.get("minimum_payment", 0),
            debt_name=debt["name"],
        )
        return {
            "debt_name": schedule.debt_name,
            "original_balance": schedule.original_balance,
            "interest_rate": schedule.interest_rate,
            "monthly_payment": schedule.monthly_payment,
            "total_interest": schedule.total_interest,
            "total_payments": schedule.total_payments,
            "payoff_months": schedule.payoff_months,
            "payoff_date": schedule.payoff_date,
            "rows": [
                {
                    "month": r.month, "payment_date": r.payment_date,
                    "payment": r.payment, "principal": r.principal,
                    "interest": r.interest, "balance": r.balance,
                    "cumulative_interest": r.cumulative_interest,
                }
                for r in schedule.rows
            ],
        }

    async def get_due_alerts(self, household_id: str):
        from datetime import date as date_type

        debts = await self.debt_repo.get_all(household_id)
        today = date_type.today()

        paid_months = {}
        for debt in debts:
            payments = await self.payment_repo.get_by_debt_id(debt["id"], limit=1000)
            months = set()
            for p in [p for p in payments if not p.get("is_reversed")]:
                pd = p["payment_date"]
                if hasattr(pd, 'year'):
                    months.add((pd.year, pd.month))
            overrides = await self.override_repo.get_by_debt_id(debt["id"])
            for o in overrides:
                if o["is_paid"]:
                    months.add((o["year"], o["month"]))
            paid_months[debt["id"]] = months

        engine = AmortizationEngine()
        return engine.calculate_due_alerts(debts, paid_months=paid_months)
