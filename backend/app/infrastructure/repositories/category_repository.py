from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import CategoryModel
from app.application.interfaces.category_repository import CategoryRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id) -> list[dict]:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.household_id == _to_str_id(household_id))
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, category: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in category.items()}
        model = CategoryModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    async def update(self, category: dict) -> dict:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == _to_str_id(category["id"]))
        )
        model = result.scalar_one()
        for key, value in category.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    @staticmethod
    def _to_dict(model: CategoryModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "name": model.name,
            "type": model.type,
            "icon": model.icon,
            "color": model.color,
        }
