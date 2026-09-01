from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import UserModel
from app.application.interfaces.user_repository import UserRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_by_email(self, email: str) -> Optional[dict]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all_by_household(self, household_id) -> list[dict]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.household_id == _to_str_id(household_id))
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, user: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in user.items()}
        model = UserModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, user: dict) -> Optional[dict]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == _to_str_id(user["id"]))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        for key, value in user.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    @staticmethod
    def _to_dict(model: UserModel) -> dict:
        return {
            "id": model.id,
            "email": model.email,
            "name": model.name,
            "password_hash": model.password_hash,
            "role": model.role,
            "household_id": model.household_id,
            "created_at": model.created_at,
        }
