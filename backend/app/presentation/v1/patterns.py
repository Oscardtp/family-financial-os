from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member
from app.presentation.schemas.schemas import (
    DetectedPatternResponse, PatternConfirmRequest,
)
from app.application.services.pattern_service import PatternService

router = APIRouter(prefix="/patterns", tags=["Patterns"])


@router.get("", response_model=list[DetectedPatternResponse])
async def list_patterns(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = PatternService(db)
    return await service.get_patterns(current_user["household_id"])


@router.get("/unconfirmed", response_model=list[DetectedPatternResponse])
async def list_unconfirmed_patterns(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = PatternService(db)
    return await service.get_unconfirmed(current_user["household_id"])


@router.post("/detect")
async def detect_patterns(
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = PatternService(db)
    patterns = await service.persist_patterns(current_user["household_id"])
    return {"detected": len(patterns), "patterns": patterns}


@router.post("/{pattern_id}/confirm")
async def confirm_pattern(
    pattern_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = PatternService(db)
    result = await service.confirm_pattern(pattern_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Patrón no encontrado")
    return result


@router.post("/{pattern_id}/reject")
async def reject_pattern(
    pattern_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = PatternService(db)
    result = await service.reject_pattern(pattern_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Patrón no encontrado")
    return result
