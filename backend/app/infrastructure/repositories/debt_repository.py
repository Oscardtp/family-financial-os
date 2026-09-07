from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import DebtModel
from app.application.interfaces.debt_repository import DebtRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyDebtRepository(DebtRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(DebtModel).where(DebtModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(DebtModel)
            .where(DebtModel.household_id == _to_str_id(household_id))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, debt: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in debt.items()}
        model = DebtModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, debt: dict) -> dict:
        result = await self.session.execute(
            select(DebtModel).where(DebtModel.id == _to_str_id(debt["id"]))
        )
        model = result.scalar_one()
        for key, value in debt.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(DebtModel).where(DebtModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    async def get_total_balance(self, household_id):
        result = await self.session.execute(
            select(func.sum(DebtModel.current_balance))
            .where(DebtModel.household_id == _to_str_id(household_id))
            .where(DebtModel.status.in_(["active", "paused"]))
        )
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")

    @staticmethod
    def _to_dict(model: DebtModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "name": model.name,
            "creditor": model.creditor,
            "total_amount": Decimal(str(model.total_amount)),
            "current_balance": Decimal(str(model.current_balance)),
            "interest_rate": Decimal(str(model.interest_rate)),
            "interest_rate_type": model.interest_rate_type if hasattr(model, 'interest_rate_type') else "EA",
            "minimum_payment": Decimal(str(model.minimum_payment)),
            "due_day": model.due_day,
            "start_date": model.start_date,
            "end_date": model.end_date,
            "status": model.status,
        }
