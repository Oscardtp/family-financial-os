from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import AccountBalanceHistoryModel


class SQLAlchemyAccountBalanceHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        model = AccountBalanceHistoryModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def get_by_account(
        self, account_id: str, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        result = await self.session.execute(
            select(AccountBalanceHistoryModel)
            .where(AccountBalanceHistoryModel.account_id == account_id)
            .order_by(desc(AccountBalanceHistoryModel.recorded_at))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_latest_by_account(self, account_id: str) -> Optional[dict]:
        result = await self.session.execute(
            select(AccountBalanceHistoryModel)
            .where(AccountBalanceHistoryModel.account_id == account_id)
            .order_by(desc(AccountBalanceHistoryModel.recorded_at))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_balance_at_date(
        self, account_id: str, target_date
    ) -> Optional[dict]:
        result = await self.session.execute(
            select(AccountBalanceHistoryModel)
            .where(AccountBalanceHistoryModel.account_id == account_id)
            .where(AccountBalanceHistoryModel.recorded_at <= target_date)
            .order_by(desc(AccountBalanceHistoryModel.recorded_at))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    @staticmethod
    def _to_dict(model: AccountBalanceHistoryModel) -> dict:
        return {
            "id": model.id,
            "account_id": model.account_id,
            "transaction_id": model.transaction_id,
            "balance_before": Decimal(str(model.balance_before)),
            "balance_after": Decimal(str(model.balance_after)),
            "change_amount": Decimal(str(model.change_amount)),
            "change_type": model.change_type,
            "recorded_at": model.recorded_at,
        }
