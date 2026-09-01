from typing import Optional
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import FinancialEventModel


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyFinancialEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(FinancialEventModel).where(FinancialEventModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .order_by(FinancialEventModel.due_date)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_by_month(self, household_id, year: int, month: int) -> list[dict]:
        if month == 12:
            date_from = date(year, 12, 1)
            date_to = date(year + 1, 1, 1)
        else:
            date_from = date(year, month, 1)
            date_to = date(year, month + 1, 1)
        return await self.get_by_date_range(household_id, date_from, date_to)

    async def get_by_date_range(self, household_id, date_from: date, date_to: date) -> list[dict]:
        result = await self.session.execute(
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .where(and_(
                FinancialEventModel.due_date >= date_from,
                FinancialEventModel.due_date < date_to,
            ))
            .order_by(FinancialEventModel.due_date)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_pending(self, household_id) -> list[dict]:
        result = await self.session.execute(
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .where(FinancialEventModel.status == "pending")
            .order_by(FinancialEventModel.due_date)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_overdue(self, household_id, as_of: date) -> list[dict]:
        result = await self.session.execute(
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .where(FinancialEventModel.status == "pending")
            .where(FinancialEventModel.due_date < as_of)
            .order_by(FinancialEventModel.due_date)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, data: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        model = FinancialEventModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, data: dict) -> dict:
        result = await self.session.execute(
            select(FinancialEventModel).where(FinancialEventModel.id == _to_str_id(data["id"]))
        )
        model = result.scalar_one()
        for key, value in data.items():
            if key != "id":
                setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(FinancialEventModel).where(FinancialEventModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    async def mark_as_paid(self, id_val, paid_by: str, paid_amount: float, paid_at) -> dict:
        result = await self.session.execute(
            select(FinancialEventModel).where(FinancialEventModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.status = "paid"
        model.paid_by = paid_by
        model.paid_amount = paid_amount
        model.paid_at = paid_at
        model.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def exists_for_source(self, household_id, source: str, source_id: str, due_date: date) -> bool:
        result = await self.session.execute(
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .where(FinancialEventModel.source == source)
            .where(FinancialEventModel.source_id == source_id)
            .where(FinancialEventModel.due_date == due_date)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_recurrence_group(self, household_id, recurrence_group_id: str) -> list[dict]:
        result = await self.session.execute(
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .where(FinancialEventModel.recurrence_group_id == recurrence_group_id)
            .order_by(FinancialEventModel.due_date)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_upcoming(self, household_id, as_of: date, days: int = 30, include_overdue: bool = False) -> list[dict]:
        from datetime import timedelta
        date_to = as_of + timedelta(days=days)
        query = (
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .where(FinancialEventModel.status == "pending")
            .where(FinancialEventModel.due_date <= date_to)
        )
        if not include_overdue:
            query = query.where(FinancialEventModel.due_date >= as_of)
        result = await self.session.execute(query.order_by(FinancialEventModel.due_date))
        return [self._to_dict(m) for m in result.scalars().all()]

    async def delete_upcoming_by_obligation(self, household_id, obligation_id: str, as_of: date) -> int:
        result = await self.session.execute(
            select(FinancialEventModel)
            .where(FinancialEventModel.household_id == _to_str_id(household_id))
            .where(FinancialEventModel.obligation_id == obligation_id)
            .where(FinancialEventModel.status == "pending")
            .where(FinancialEventModel.due_date >= as_of)
        )
        models = result.scalars().all()
        count = 0
        for model in models:
            await self.session.delete(model)
            count += 1
        await self.session.flush()
        return count

    @staticmethod
    def _to_dict(model: FinancialEventModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "source": model.source,
            "source_id": model.source_id,
            "type": model.type,
            "title": model.title,
            "amount": model.amount,
            "currency": model.currency,
            "due_date": model.due_date,
            "recommended_date": model.recommended_date,
            "cutoff_date": model.cutoff_date,
            "status": model.status,
            "account_id": model.account_id,
            "responsible_member_id": model.responsible_member_id,
            "is_recurrent": model.is_recurrent,
            "recurrence_group_id": model.recurrence_group_id,
            "reminder_days_before": model.reminder_days_before,
            "notes": model.notes,
            "confirmed": model.confirmed,
            "paid_at": model.paid_at,
            "paid_amount": model.paid_amount,
            "paid_by": model.paid_by,
            "obligation_id": model.obligation_id,
            "category_id": model.category_id,
            "visibility": model.visibility,
            "confidence": model.confidence,
            "payment_method": model.payment_method,
            "consequence_note": model.consequence_note,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }
