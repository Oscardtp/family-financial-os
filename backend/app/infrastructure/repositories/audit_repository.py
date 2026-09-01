from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.models import AuditLogModel


class SQLAlchemyAuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, log_data: dict) -> dict:
        model = AuditLogModel(**log_data)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def get_all(self, household_id: str, skip: int = 0, limit: int = 50) -> list[dict]:
        result = await self.session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.household_id == household_id)
            .order_by(desc(AuditLogModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    @staticmethod
    def _to_dict(model: AuditLogModel) -> dict:
        return {
            "id": model.id,
            "household_id": model.household_id,
            "user_id": model.user_id,
            "user_email": model.user_email,
            "action": model.action,
            "entity_type": model.entity_type,
            "entity_id": model.entity_id,
            "entity_name": model.entity_name,
            "details": model.details,
            "created_at": model.created_at,
        }
