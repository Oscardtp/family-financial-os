from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import DetectedPatternModel
from app.infrastructure.datetime_utils import utc_now_naive


class SQLAlchemyDetectedPatternRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        model = DetectedPatternModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def get_by_household(
        self, household_id: str, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        result = await self.session.execute(
            select(DetectedPatternModel)
            .where(DetectedPatternModel.household_id == household_id)
            .order_by(desc(DetectedPatternModel.confidence))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_unconfirmed(self, household_id: str) -> list[dict]:
        result = await self.session.execute(
            select(DetectedPatternModel)
            .where(DetectedPatternModel.household_id == household_id)
            .where(DetectedPatternModel.is_confirmed == False)
            .where(DetectedPatternModel.is_rejected == False)
            .order_by(desc(DetectedPatternModel.confidence))
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def confirm(self, pattern_id: str) -> Optional[dict]:
        result = await self.session.execute(
            select(DetectedPatternModel)
            .where(DetectedPatternModel.id == pattern_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_confirmed = True
            model.is_rejected = False
            model.updated_at = utc_now_naive()
            await self.session.flush()
            await self.session.refresh(model)
        return self._to_dict(model) if model else None

    async def reject(self, pattern_id: str) -> Optional[dict]:
        result = await self.session.execute(
            select(DetectedPatternModel)
            .where(DetectedPatternModel.id == pattern_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_rejected = True
            model.is_confirmed = False
            model.updated_at = utc_now_naive()
            await self.session.flush()
            await self.session.refresh(model)
        return self._to_dict(model) if model else None

    async def find_existing(
        self, household_id: str, name: str, pattern_type: str
    ) -> Optional[dict]:
        result = await self.session.execute(
            select(DetectedPatternModel)
            .where(DetectedPatternModel.household_id == household_id)
            .where(DetectedPatternModel.name == name)
            .where(DetectedPatternModel.type == pattern_type)
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def update(self, pattern_id: str, data: dict) -> Optional[dict]:
        result = await self.session.execute(
            select(DetectedPatternModel)
            .where(DetectedPatternModel.id == pattern_id)
        )
        model = result.scalar_one_or_none()
        if model:
            for key, value in data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            model.updated_at = utc_now_naive()
            await self.session.flush()
            await self.session.refresh(model)
        return self._to_dict(model) if model else None

    @staticmethod
    def _to_dict(model: DetectedPatternModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "name": model.name,
            "type": model.type,
            "avg_amount": Decimal(str(model.avg_amount)),
            "avg_day_of_month": model.avg_day_of_month,
            "frequency": model.frequency,
            "occurrences": model.occurrences,
            "confidence": model.confidence,
            "source": model.source,
            "source_id": model.source_id,
            "category_id": model.category_id,
            "account_id": model.account_id,
            "first_seen": model.first_seen,
            "last_seen": model.last_seen,
            "is_confirmed": model.is_confirmed,
            "is_rejected": model.is_rejected,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }
