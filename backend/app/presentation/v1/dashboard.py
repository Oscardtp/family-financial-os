from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer
from app.presentation.schemas.schemas import DashboardResponse
from app.application.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse, summary="Dashboard summary", description="Returns financial overview: balance, income, expenses, net worth, recent transactions, budget status")
async def get_dashboard(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    return await service.get_summary(current_user)
