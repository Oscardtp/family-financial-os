import uuid
from decimal import Decimal
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import DebtPaymentModel
from app.application.interfaces.debt_payment_repository import DebtPaymentRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyDebtPaymentRepository(DebtPaymentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_debt_id(self, debt_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(DebtPaymentModel)
            .where(DebtPaymentModel.debt_id == _to_str_id(debt_id))
            .order_by(DebtPaymentModel.payment_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_by_id(self, payment_id: str) -> dict | None:
        result = await self.session.execute(
            select(DebtPaymentModel)
            .where(DebtPaymentModel.id == payment_id)
        )
        row = result.scalar_one_or_none()
        return self._to_dict(row) if row else None

    async def create(self, payment: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in payment.items()}
        model = DebtPaymentModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def find_by_debt_and_month(self, debt_id: str, year: int, month: int) -> dict | None:
        from datetime import date as date_type
        if month == 12:
            date_from = date_type(year, 12, 1)
            date_to = date_type(year + 1, 1, 1)
        else:
            date_from = date_type(year, month, 1)
            date_to = date_type(year, month + 1, 1)
        result = await self.session.execute(
            select(DebtPaymentModel)
            .where(DebtPaymentModel.debt_id == _to_str_id(debt_id))
            .where(DebtPaymentModel.payment_date >= date_from)
            .where(DebtPaymentModel.payment_date < date_to)
            .where(DebtPaymentModel.is_reversed == False)  # noqa: E712
            .order_by(DebtPaymentModel.payment_date.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return self._to_dict(row) if row else None

    async def reverse(self, payment_id: str) -> None:
        await self.session.execute(
            update(DebtPaymentModel)
            .where(DebtPaymentModel.id == payment_id)
            .values(is_reversed=True)
        )
        await self.session.flush()

    async def unreverse(self, payment_id: str) -> None:
        await self.session.execute(
            update(DebtPaymentModel)
            .where(DebtPaymentModel.id == payment_id)
            .values(is_reversed=False)
        )
        await self.session.flush()

    @staticmethod
    def _to_dict(model: DebtPaymentModel) -> dict:
        return {
            "id": model.id,
            "debt_id": model.debt_id,
            "amount": Decimal(str(model.amount)),
            "principal": Decimal(str(model.principal)) if model.principal else None,
            "interest": Decimal(str(model.interest)) if model.interest else None,
            "payment_date": model.payment_date,
            "is_reversed": model.is_reversed,
        }
