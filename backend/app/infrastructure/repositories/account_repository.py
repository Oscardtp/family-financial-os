from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import AccountModel
from app.application.interfaces.account_repository import AccountRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(self, household_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(AccountModel)
            .where(AccountModel.household_id == _to_str_id(household_id))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, account: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in account.items()}
        model = AccountModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def update(self, account: dict) -> Optional[dict]:
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == _to_str_id(account["id"]))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        for key, value in account.items():
            if key != "id":
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    async def update_balance(self, id_val, amount) -> dict:
        await self.session.execute(
            update(AccountModel)
            .where(AccountModel.id == _to_str_id(id_val))
            .values(balance=AccountModel.balance + Decimal(str(amount)))
        )
        await self.session.flush()
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one()
        return self._to_dict(model)

    async def deduct_balance(self, id_val, amount) -> Optional[dict]:
        result = await self.session.execute(
            update(AccountModel)
            .where(AccountModel.id == _to_str_id(id_val))
            .where(AccountModel.balance >= Decimal(str(amount)))
            .values(balance=AccountModel.balance - Decimal(str(amount)))
        )
        await self.session.flush()
        if result.rowcount == 0:
            return None
        return await self.get_by_id(id_val)

    @staticmethod
    def _to_dict(model: AccountModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "name": model.name,
            "type": model.type,
            "balance": Decimal(str(model.balance)),
            "currency": model.currency,
            "is_active": model.is_active,
            "created_at": model.created_at,
        }
