from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer
from app.infrastructure.repositories.balance_history_repository import SQLAlchemyAccountBalanceHistoryRepository
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository

router = APIRouter(prefix="/balance-history", tags=["Balance History"])


@router.get("/{account_id}")
async def get_balance_history(
    account_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    account_repo = SQLAlchemyAccountRepository(db)
    account = await account_repo.get_by_id(account_id)
    if not account or account["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    history_repo = SQLAlchemyAccountBalanceHistoryRepository(db)
    history = await history_repo.get_by_account(account_id, skip, limit)
    return {
        "account_id": account_id,
        "current_balance": account["balance"],
        "history": history,
    }


@router.get("/{account_id}/at/{target_date}")
async def get_balance_at_date(
    account_id: str,
    target_date: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    from datetime import date as DateType
    account_repo = SQLAlchemyAccountRepository(db)
    account = await account_repo.get_by_id(account_id)
    if not account or account["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    history_repo = SQLAlchemyAccountBalanceHistoryRepository(db)
    target = DateType.fromisoformat(target_date)
    history = await history_repo.get_balance_at_date(account_id, target)
    if not history:
        return {"account_id": account_id, "balance_at_date": None, "record": None}
    return {
        "account_id": account_id,
        "balance_at_date": history["balance_after"],
        "record": history,
    }
