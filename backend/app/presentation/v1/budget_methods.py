from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member
from app.presentation.schemas.schemas import (
    HouseholdMethodConfigSchema,
    MethodConfigResponse,
    MethodPresetSchema,
    MethodPreviewRequest,
    MethodPreviewResponse,
)
from app.application.services.budget_method_service import BudgetMethodService

router = APIRouter(tags=["Budget Method"])


@router.get(
    "/budget-methods/presets",
    response_model=list[MethodPresetSchema],
    summary="List budget method presets",
    description="Static catalog from the domain. Never persisted as household data.",
)
async def list_method_presets(
    current_user: dict = Depends(require_viewer),
):
    service = BudgetMethodService(db=None)
    return service.presets()


@router.get(
    "/budget-method",
    response_model=MethodConfigResponse,
    summary="Get household method configuration",
    description="Returns the saved configuration or empty defaults.",
)
async def get_method_config(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetMethodService(db)
    return await service.get_config(current_user["household_id"])


@router.put(
    "/budget-method",
    response_model=MethodConfigResponse,
    summary="Save household method configuration",
    description="Persists only the method configuration. Existing budgets are never modified.",
)
async def save_method_config(
    data: HouseholdMethodConfigSchema,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetMethodService(db)
    try:
        result = await service.save_config(current_user["household_id"], data)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/budget-method/preview",
    response_model=MethodPreviewResponse,
    summary="Preview a method distribution",
    description="Backend-computed preview. Nothing is persisted.",
)
async def preview_method(
    data: MethodPreviewRequest,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetMethodService(db)
    try:
        return service.preview(data.income_amount, data.groups)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
