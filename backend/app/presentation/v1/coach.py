from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer
from app.application.services.learning_service import LearningService

router = APIRouter(prefix="/coach", tags=["Coach"])


@router.get("/suggestions")
async def suggestions(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = LearningService(db)
    return await service.detect_patterns(current_user["household_id"])


@router.get("/patterns")
async def patterns(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = LearningService(db)
    return await service.detect_patterns(current_user["household_id"])
