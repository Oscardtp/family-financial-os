from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.presentation.schemas.schemas import (
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse,
    SavingsContributionCreate, SavingsContributionResponse,
    GoalProjectionRequest, GoalProjectionResponse,
)
from app.application.services.savings_service import SavingsService

router = APIRouter(prefix="/savings", tags=["Savings"])


@router.get("/summary", summary="Savings summary", description="Returns savings overview with rate and goal progress")
async def savings_summary(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    return await service.get_summary(current_user["household_id"])


@router.get("/goals", response_model=list[SavingsGoalResponse], summary="List savings goals", description="Returns all savings goals with progress")
async def list_goals(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    return await service.list_goals(current_user["household_id"], skip, limit)


@router.post("/goals", response_model=SavingsGoalResponse, status_code=201, summary="Create savings goal", description="Set a new savings target")
async def create_goal(
    data: SavingsGoalCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    result = await service.create_goal(data, current_user["household_id"])
    await db.commit()
    return result


@router.get("/goals/{goal_id}", response_model=SavingsGoalResponse, summary="Get goal details", description="Returns full details of a specific savings goal")
async def get_goal(
    goal_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    try:
        return await service.get_goal(goal_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta meta")


@router.put("/goals/{goal_id}", response_model=SavingsGoalResponse, summary="Update goal", description="Modify savings goal details")
async def update_goal(
    goal_id: str,
    data: SavingsGoalUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    try:
        result = await service.update_goal(goal_id, data, current_user["household_id"])
        await db.commit()
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta meta")


@router.delete("/goals/{goal_id}", status_code=204, summary="Delete goal", description="Remove a savings goal")
async def delete_goal(
    goal_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    try:
        await service.delete_goal(goal_id, current_user["household_id"])
        await db.commit()
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta meta")


@router.post("/goals/{goal_id}/contributions", response_model=SavingsContributionResponse, status_code=201, summary="Record contribution", description="Add money toward a savings goal")
async def create_contribution(
    goal_id: str,
    data: SavingsContributionCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    try:
        result = await service.create_contribution(goal_id, data, current_user["household_id"])
        await db.commit()
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta meta")


@router.get("/goals/{goal_id}/contributions", response_model=list[SavingsContributionResponse], summary="List contributions", description="Returns all contributions made toward a savings goal")
async def list_contributions(
    goal_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = SavingsService(db)
    try:
        return await service.list_contributions(goal_id, current_user["household_id"], skip, limit)
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta meta")


@router.post(
    "/goals/projection",
    response_model=GoalProjectionResponse,
    summary="Project goal completion",
    description="Calculate when a goal will be reached based on current amount, monthly contribution, and optional return rate",
)
async def project_goal(
    data: GoalProjectionRequest,
    current_user: dict = Depends(require_viewer),
):
    service = SavingsService(None)
    return service.project_goal(data)
