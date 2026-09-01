from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import BudgetModel
from app.application.interfaces.budget_repository import BudgetRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyBudgetRepository(BudgetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(BudgetModel).where(BudgetModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, month: int, year: int) -> list[dict]:
        result = await self.session.execute(
            select(BudgetModel)
            .where(BudgetModel.household_id == _to_str_id(household_id))
            .where(BudgetModel.month == month)
            .where(BudgetModel.year == year)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_by_category_and_period(
        self, household_id, category_id, month: int, year: int
    ) -> Optional[dict]:
        result = await self.session.execute(
            select(BudgetModel)
            .where(BudgetModel.household_id == _to_str_id(household_id))
            .where(BudgetModel.category_id == _to_str_id(category_id))
            .where(BudgetModel.month == month)
            .where(BudgetModel.year == year)
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def create(self, budget: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in budget.items()}
        model = BudgetModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, budget: dict) -> dict:
        result = await self.session.execute(
            select(BudgetModel).where(BudgetModel.id == _to_str_id(budget["id"]))
        )
        model = result.scalar_one()
        for key, value in budget.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(BudgetModel).where(BudgetModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    @staticmethod
    def _to_dict(model: BudgetModel) -> dict:
        return {
            "id": model.id,
            "category_id": model.category_id,
            "household_id": model.household_id,
            "amount": float(model.amount),
            "month": model.month,
            "year": model.year,
        }
