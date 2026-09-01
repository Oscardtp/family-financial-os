from typing import Optional
import uuid
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import RecurringPaymentModel


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyRecurringPaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(RecurringPaymentModel).where(RecurringPaymentModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(RecurringPaymentModel)
            .where(RecurringPaymentModel.household_id == _to_str_id(household_id))
            .order_by(RecurringPaymentModel.next_due_date)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_active(self, household_id) -> list[dict]:
        result = await self.session.execute(
            select(RecurringPaymentModel)
            .where(RecurringPaymentModel.household_id == _to_str_id(household_id))
            .where(RecurringPaymentModel.is_active == True)
            .order_by(RecurringPaymentModel.next_due_date)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_due_today(self, household_id, today: date) -> list[dict]:
        result = await self.session.execute(
            select(RecurringPaymentModel)
            .where(RecurringPaymentModel.household_id == _to_str_id(household_id))
            .where(RecurringPaymentModel.is_active == True)
            .where(RecurringPaymentModel.next_due_date <= today)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, data: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        model = RecurringPaymentModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, data: dict) -> dict:
        result = await self.session.execute(
            select(RecurringPaymentModel).where(RecurringPaymentModel.id == _to_str_id(data["id"]))
        )
        model = result.scalar_one()
        for key, value in data.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(RecurringPaymentModel).where(RecurringPaymentModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    @staticmethod
    def _to_dict(model: RecurringPaymentModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "account_id": model.account_id,
            "category_id": model.category_id,
            "name": model.name,
            "amount": float(model.amount),
            "type": model.type,
            "frequency": model.frequency,
            "day_of_month": model.day_of_month,
            "next_due_date": model.next_due_date,
            "is_active": model.is_active,
            "description": model.description,
            "created_at": model.created_at,
        }
