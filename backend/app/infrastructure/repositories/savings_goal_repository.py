from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import SavingsGoalModel
from app.application.interfaces.savings_goal_repository import SavingsGoalRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemySavingsGoalRepository(SavingsGoalRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(SavingsGoalModel).where(SavingsGoalModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(SavingsGoalModel)
            .where(SavingsGoalModel.household_id == _to_str_id(household_id))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, goal: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in goal.items()}
        model = SavingsGoalModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, goal: dict) -> dict:
        result = await self.session.execute(
            select(SavingsGoalModel).where(SavingsGoalModel.id == _to_str_id(goal["id"]))
        )
        model = result.scalar_one()
        for key, value in goal.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(SavingsGoalModel).where(SavingsGoalModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    @staticmethod
    def _to_dict(model: SavingsGoalModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "name": model.name,
            "target_amount": Decimal(str(model.target_amount)),
            "current_amount": Decimal(str(model.current_amount)),
            "target_date": model.target_date,
            "monthly_contribution": Decimal(str(model.monthly_contribution)) if model.monthly_contribution is not None else None,
            "priority": model.priority,
            "goal_type": model.goal_type or "savings",
            "expected_return_rate": Decimal(str(model.expected_return_rate)) if model.expected_return_rate is not None else None,
            "horizon_months": model.horizon_months,
        }
