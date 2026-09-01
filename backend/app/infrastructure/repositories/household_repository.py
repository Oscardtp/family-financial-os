from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import HouseholdModel, UserModel
from app.application.interfaces.household_repository import HouseholdRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyHouseholdRepository(HouseholdRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(HouseholdModel).where(HouseholdModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def create(self, household: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in household.items()}
        model = HouseholdModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def add_member(self, household_id, user_id, role: str = "member") -> dict:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == _to_str_id(user_id))
        )
        user = result.scalar_one()
        user.household_id = _to_str_id(household_id)
        user.role = role
        await self.session.flush()
        return {"household_id": _to_str_id(household_id), "user_id": _to_str_id(user_id), "role": role}

    @staticmethod
    def _to_dict(model: HouseholdModel) -> dict:
        return {
            "id": model.id,
            "name": model.name,
            "created_at": model.created_at,
        }
