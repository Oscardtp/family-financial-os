import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import DebtPaymentOverrideModel
from app.application.interfaces.debt_payment_override_repository import DebtPaymentOverrideRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyDebtPaymentOverrideRepository(DebtPaymentOverrideRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_debt_and_month(self, debt_id: str, year: int, month: int) -> dict | None:
        result = await self.session.execute(
            select(DebtPaymentOverrideModel)
            .where(
                DebtPaymentOverrideModel.debt_id == debt_id,
                DebtPaymentOverrideModel.year == year,
                DebtPaymentOverrideModel.month == month,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_dict(row) if row else None

    async def get_by_debt_id(self, debt_id: str) -> list[dict]:
        result = await self.session.execute(
            select(DebtPaymentOverrideModel)
            .where(DebtPaymentOverrideModel.debt_id == debt_id)
            .order_by(DebtPaymentOverrideModel.year.desc(), DebtPaymentOverrideModel.month.desc())
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, override: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in override.items()}
        model = DebtPaymentOverrideModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    @staticmethod
    def _to_dict(model: DebtPaymentOverrideModel) -> dict:
        return {
            "id": model.id,
            "debt_id": model.debt_id,
            "year": model.year,
            "month": model.month,
            "is_paid": model.is_paid,
            "marked_by": model.marked_by,
            "marked_at": model.marked_at,
        }
