import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import SavingsContributionModel
from app.application.interfaces.savings_contribution_repository import SavingsContributionRepository


def _to_str_id(id_val) -> str:
    return str(id_val) if id_val is not None else None


class SQLAlchemySavingsContributionRepository(SavingsContributionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_goal_id(self, goal_id, skip: int = 0, limit: int = 100) -> list[dict]:
        result = await self.session.execute(
            select(SavingsContributionModel)
            .where(SavingsContributionModel.goal_id == _to_str_id(goal_id))
            .order_by(SavingsContributionModel.contribution_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def create(self, contribution: dict) -> dict:
        clean = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in contribution.items()}
        model = SavingsContributionModel(**clean)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    @staticmethod
    def _to_dict(model: SavingsContributionModel) -> dict:
        return {
            "id": model.id,
            "goal_id": model.goal_id,
            "amount": float(model.amount),
            "contribution_date": model.contribution_date,
        }
