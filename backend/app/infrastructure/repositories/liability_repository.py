from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import LiabilityModel
from app.application.interfaces.liability_repository import LiabilityRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyLiabilityRepository(LiabilityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(LiabilityModel).where(LiabilityModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(LiabilityModel)
            .where(LiabilityModel.household_id == _to_str_id(household_id))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, liability: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in liability.items()}
        model = LiabilityModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, liability: dict) -> dict:
        result = await self.session.execute(
            select(LiabilityModel).where(LiabilityModel.id == _to_str_id(liability["id"]))
        )
        model = result.scalar_one()
        for key, value in liability.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(LiabilityModel).where(LiabilityModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    async def get_total_balance(self, household_id):
        result = await self.session.execute(
            select(func.sum(LiabilityModel.current_balance))
            .where(LiabilityModel.household_id == _to_str_id(household_id))
        )
        total = result.scalar()
        return Decimal(str(total)) if total else Decimal("0")

    @staticmethod
    def _to_dict(model: LiabilityModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "name": model.name,
            "type": model.type,
            "total_amount": Decimal(str(model.total_amount)),
            "current_balance": Decimal(str(model.current_balance)),
            "interest_rate": Decimal(str(model.interest_rate)),
            "monthly_payment": Decimal(str(model.monthly_payment)),
        }
