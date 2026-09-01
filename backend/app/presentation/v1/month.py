from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer
from app.application.services.calendar_service import CalendarService
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.application.interfaces.transaction_repository import TransactionRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository

router = APIRouter(prefix="/month", tags=["Month"])


@router.get("/prepare")
async def prepare_month(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(
        db,
        account_repo=SQLAlchemyAccountRepository(db),
        event_repo=SQLAlchemyFinancialEventRepository(db),
        budget_repo=SQLAlchemyBudgetRepository(db),
        tx_repo=SQLAlchemyTransactionRepository(db),
    )
    return await service.prepare_month(current_user["household_id"])
