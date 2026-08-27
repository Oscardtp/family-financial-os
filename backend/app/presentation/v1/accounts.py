from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.presentation.schemas.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
)
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.presentation.audit_helper import log_action

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=list[AccountResponse], summary="List all accounts", description="Returns all financial accounts for the household")
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAccountRepository(db)
    return await repo.get_all(current_user["household_id"], skip, limit)


@router.post("", response_model=AccountResponse, status_code=201, summary="Create account", description="Create a new financial account (bank, cash, investment, etc.)")
async def create_account(
    data: AccountCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAccountRepository(db)
    result = await repo.create({
        "household_id": current_user["household_id"],
        **data.model_dump(),
    })
    await log_action(
        db, current_user["household_id"], current_user["id"], current_user["email"],
        "create", "account", result["id"], result["name"],
    )
    return result


@router.get("/{account_id}", response_model=AccountResponse, summary="Get account details", description="Returns full details of a specific account")
async def get_account(
    account_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAccountRepository(db)
    account = await repo.get_by_id(account_id)
    if not account or account["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos esta cuenta")
    return account


@router.put("/{account_id}", response_model=AccountResponse, summary="Update account", description="Update account information (name, type, balance, etc.)")
async def update_account(
    account_id: str,
    data: AccountUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAccountRepository(db)
    account = await repo.get_by_id(account_id)
    if not account or account["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos esta cuenta")

    update_data = data.model_dump(exclude_unset=True)
    result = await repo.update({**account, **update_data})
    await log_action(
        db, current_user["household_id"], current_user["id"], current_user["email"],
        "update", "account", result["id"], result["name"],
    )
    return result


@router.delete("/{account_id}", status_code=204, summary="Delete account", description="Permanently delete an account")
async def delete_account(
    account_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAccountRepository(db)
    account = await repo.get_by_id(account_id)
    if not account or account["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos esta cuenta")
    await repo.delete(account_id)
    await log_action(
        db, current_user["household_id"], current_user["id"], current_user["email"],
        "delete", "account", account_id, account["name"],
    )
