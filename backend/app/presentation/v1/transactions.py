from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.presentation.schemas.schemas import TransactionCreate, TransactionResponse
from app.application.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=list[TransactionResponse], summary="List transactions", description="Returns all transactions with optional filters")
async def list_transactions(
    account_id: str | None = None,
    category_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = TransactionService(db)
    return await service.list(
        household_id=current_user["household_id"],
        account_id=account_id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=TransactionResponse, status_code=201, summary="Create transaction", description="Record a new income, expense, or transfer")
async def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = TransactionService(db)
    try:
        return await service.create(data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}", status_code=204, summary="Delete transaction", description="Remove a transaction record")
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = TransactionService(db)
    try:
        await service.delete(transaction_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
