from typing import Optional
import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import FinancialObligationModel


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyFinancialObligationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(FinancialObligationModel).where(FinancialObligationModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(FinancialObligationModel)
            .where(FinancialObligationModel.household_id == _to_str_id(household_id))
            .order_by(FinancialObligationModel.name)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_active(self, household_id) -> list[dict]:
        result = await self.session.execute(
            select(FinancialObligationModel)
            .where(FinancialObligationModel.household_id == _to_str_id(household_id))
            .where(FinancialObligationModel.is_active == True)  # noqa: E712
            .order_by(FinancialObligationModel.name)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_by_source(self, household_id, source: str, source_id: str) -> Optional[dict]:
        result = await self.session.execute(
            select(FinancialObligationModel)
            .where(FinancialObligationModel.household_id == _to_str_id(household_id))
            .where(FinancialObligationModel.source == source)
            .where(FinancialObligationModel.source_id == source_id)
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def create(self, data: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        model = FinancialObligationModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, data: dict) -> dict:
        result = await self.session.execute(
            select(FinancialObligationModel).where(
                FinancialObligationModel.id == _to_str_id(data["id"])
            )
        )
        model = result.scalar_one()
        for key, value in data.items():
            if key != "id":
                setattr(model, key, value)
        model.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(FinancialObligationModel).where(
                FinancialObligationModel.id == _to_str_id(id_val)
            )
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    @staticmethod
    def _to_dict(model: FinancialObligationModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "source": model.source,
            "source_id": model.source_id,
            "name": model.name,
            "type": model.type,
            "amount": Decimal(str(model.amount)),
            "currency": model.currency,
            "frequency": model.frequency,
            "anchor_day": model.anchor_day,
            "recommended_offset_days": model.recommended_offset_days,
            "cutoff_offset_days": model.cutoff_offset_days,
            "reminder_days_before": model.reminder_days_before,
            "account_id": model.account_id,
            "category_id": model.category_id,
            "responsible_member_id": model.responsible_member_id,
            "is_active": model.is_active,
            "confidence": model.confidence,
            "notes": model.notes,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }
