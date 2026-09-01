import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import CategoryAccountPreferenceModel
from app.application.interfaces.category_account_preference_repository import CategoryAccountPreferenceRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyCategoryAccountPreferenceRepository(CategoryAccountPreferenceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_category(self, household_id, category_id) -> dict | None:
        result = await self.session.execute(
            select(CategoryAccountPreferenceModel).where(
                CategoryAccountPreferenceModel.household_id == _to_str_id(household_id),
                CategoryAccountPreferenceModel.category_id == _to_str_id(category_id),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id) -> list[dict]:
        result = await self.session.execute(
            select(CategoryAccountPreferenceModel).where(
                CategoryAccountPreferenceModel.household_id == _to_str_id(household_id)
            )
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create_or_update(self, preference: dict) -> dict:
        existing = await self.get_by_category(
            preference["household_id"],
            preference["category_id"],
        )

        if existing:
            result = await self.session.execute(
                select(CategoryAccountPreferenceModel).where(
                    CategoryAccountPreferenceModel.id == existing["id"]
                )
            )
            model = result.scalar_one()
            model.account_id = _to_str_id(preference["account_id"])
        else:
            clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in preference.items()}
            model = CategoryAccountPreferenceModel(**clean)
            self.session.add(model)

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, household_id, category_id) -> bool:
        result = await self.session.execute(
            select(CategoryAccountPreferenceModel).where(
                CategoryAccountPreferenceModel.household_id == _to_str_id(household_id),
                CategoryAccountPreferenceModel.category_id == _to_str_id(category_id),
            )
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    @staticmethod
    def _to_dict(model: CategoryAccountPreferenceModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "category_id": model.category_id,
            "account_id": model.account_id,
        }
