from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.presentation.schemas.schemas import BudgetCreate, BudgetUpdate, BudgetResponse
from app.application.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=list[BudgetResponse], summary="List budgets", description="Returns all budgets for the current month")
async def list_budgets(
    month: int | None = None,
    year: int | None = None,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetService(db)
    return await service.list(current_user["household_id"], month, year)


@router.get("/status", summary="Budget status with context", description="Returns budget status with explanatory messages for each category")
async def budget_status(
    month: int | None = None,
    year: int | None = None,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetService(db)
    return await service.get_status(current_user["household_id"], month, year)


@router.post("", response_model=BudgetResponse, status_code=201, summary="Create budget", description="Set a spending limit for a category")
async def create_budget(
    data: BudgetCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetService(db)
    try:
        return await service.create(data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{budget_id}", response_model=BudgetResponse, summary="Update budget", description="Modify budget amount or period")
async def update_budget(
    budget_id: str,
    data: BudgetUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetService(db)
    try:
        return await service.update(budget_id, data, current_user)
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este presupuesto")


@router.delete("/{budget_id}", status_code=204, summary="Delete budget", description="Remove a budget limit")
async def delete_budget(
    budget_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BudgetService(db)
    try:
        await service.delete(budget_id, current_user)
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este presupuesto")
