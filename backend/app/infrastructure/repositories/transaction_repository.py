from decimal import Decimal
from typing import Optional
from datetime import date
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import TransactionModel, AccountModel, CategoryModel
from app.application.interfaces.transaction_repository import TransactionRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id_val) -> Optional[dict]:
        result = await self.session.execute(
            select(TransactionModel).where(TransactionModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def get_all(
        self,
        household_id,
        account_id=None,
        category_id=None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        query = (
            select(TransactionModel)
            .join(AccountModel, TransactionModel.account_id == AccountModel.id)
            .where(AccountModel.household_id == _to_str_id(household_id))
        )
        if account_id:
            query = query.where(TransactionModel.account_id == _to_str_id(account_id))
        if category_id:
            query = query.where(TransactionModel.category_id == _to_str_id(category_id))
        if date_from:
            query = query.where(TransactionModel.date >= date_from)
        if date_to:
            query = query.where(TransactionModel.date <= date_to)
        query = query.order_by(TransactionModel.date.desc(), TransactionModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, transaction: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in transaction.items()}
        model = TransactionModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def delete(self, id_val) -> bool:
        result = await self.session.execute(
            select(TransactionModel).where(TransactionModel.id == _to_str_id(id_val))
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    async def get_totals_by_category(
        self, household_id, date_from: date, date_to: date
    ) -> list[dict]:
        result = await self.session.execute(
            select(
                TransactionModel.category_id,
                CategoryModel.name.label("category_name"),
                func.sum(TransactionModel.amount).label("total"),
                TransactionModel.type,
            )
            .join(AccountModel, TransactionModel.account_id == AccountModel.id)
            .join(CategoryModel, TransactionModel.category_id == CategoryModel.id, isouter=True)
            .where(AccountModel.household_id == _to_str_id(household_id))
            .where(TransactionModel.date >= date_from)
            .where(TransactionModel.date <= date_to)
            .where(TransactionModel.type == "expense")
            .group_by(TransactionModel.category_id, CategoryModel.name, TransactionModel.type)
        )
        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "total": Decimal(str(row.total)),
                "type": row.type,
            }
            for row in result.all()
        ]

    async def get_monthly_totals(self, household_id, year: int, month: int) -> dict:
        date_from = date(year, month, 1)
        if month == 12:
            date_to = date(year + 1, 1, 1)
        else:
            date_to = date(year, month + 1, 1)

        result = await self.session.execute(
            select(
                TransactionModel.type,
                func.sum(TransactionModel.amount).label("total"),
            )
            .join(AccountModel, TransactionModel.account_id == AccountModel.id)
            .where(AccountModel.household_id == _to_str_id(household_id))
            .where(TransactionModel.date >= date_from)
            .where(TransactionModel.date < date_to)
            .group_by(TransactionModel.type)
        )
        totals = {row.type: Decimal(str(row.total)) for row in result.all()}
        return {
            "income": totals.get("income", Decimal("0")),
            "expense": totals.get("expense", Decimal("0")),
            "net": totals.get("income", Decimal("0")) - totals.get("expense", Decimal("0")),
        }

    @staticmethod
    def _to_dict(model: TransactionModel) -> dict:
        return {
            "id": model.id,
            "account_id": model.account_id,
            "category_id": model.category_id,
            "user_id": model.user_id,
            "type": model.type,
            "amount": Decimal(str(model.amount)),
            "description": model.description,
            "date": model.date,
            "to_account_id": model.to_account_id,
            "created_at": model.created_at,
        }
