from decimal import Decimal
from typing import Optional
import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import AmortizationScheduleModel


class SQLAlchemyAmortizationScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        model = AmortizationScheduleModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def bulk_create(self, items: list[dict]) -> list[dict]:
        results = []
        for item in items:
            result = await self.create(item)
            results.append(result)
        return results

    async def get_by_debt(self, debt_id: str) -> list[dict]:
        result = await self.session.execute(
            select(AmortizationScheduleModel)
            .where(AmortizationScheduleModel.debt_id == debt_id)
            .order_by(AmortizationScheduleModel.month_number)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_unpaid_by_debt(self, debt_id: str) -> list[dict]:
        result = await self.session.execute(
            select(AmortizationScheduleModel)
            .where(AmortizationScheduleModel.debt_id == debt_id)
            .where(AmortizationScheduleModel.is_paid == False)
            .order_by(AmortizationScheduleModel.month_number)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def mark_as_paid(self, schedule_id: str) -> Optional[dict]:
        result = await self.session.execute(
            select(AmortizationScheduleModel)
            .where(AmortizationScheduleModel.id == schedule_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_paid = True
            model.paid_at = uuid.uuid4()  # placeholder, will be set by service
            await self.session.flush()
            await self.session.refresh(model)
        return self._to_dict(model) if model else None

    async def delete_by_debt(self, debt_id: str) -> bool:
        result = await self.session.execute(
            select(AmortizationScheduleModel)
            .where(AmortizationScheduleModel.debt_id == debt_id)
        )
        models = result.scalars().all()
        for model in models:
            await self.session.delete(model)
        return len(models) > 0

    @staticmethod
    def _to_dict(model: AmortizationScheduleModel) -> dict:
        return {
            "id": model.id,
            "debt_id": model.debt_id,
            "month_number": model.month_number,
            "payment_date": model.payment_date,
            "payment_amount": Decimal(str(model.payment_amount)),
            "principal_portion": Decimal(str(model.principal_portion)),
            "interest_portion": Decimal(str(model.interest_portion)),
            "remaining_balance": Decimal(str(model.remaining_balance)),
            "cumulative_interest": Decimal(str(model.cumulative_interest)),
            "is_paid": model.is_paid,
            "paid_at": model.paid_at,
            "created_at": model.created_at,
        }
