from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository

router = APIRouter(prefix="/audit", tags=["Audit Log"])


@router.get("", summary="List audit logs", description="Returns paginated audit logs for the household")
async def list_audit_logs(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAuditRepository(db)
    return await repo.get_all(current_user["household_id"], skip, limit)
