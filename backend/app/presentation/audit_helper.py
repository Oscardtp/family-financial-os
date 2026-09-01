from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository


async def log_action(
    db: AsyncSession,
    household_id: str,
    user_id: str,
    user_email: str,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    entity_name: str | None = None,
    details: str | None = None,
):
    repo = SQLAlchemyAuditRepository(db)
    await repo.create({
        "household_id": household_id,
        "user_id": user_id,
        "user_email": user_email,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "details": details,
    })
