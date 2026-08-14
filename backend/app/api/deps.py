"""Dependency injection for Family Financial OS."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.infrastructure.sqlite import SQLiteRepository
from app.application.use_cases import (
    TransactionUseCase, BudgetUseCase, DebtUseCase, GoalUseCase,
    AccountUseCase, AssetUseCase, LiabilityUseCase, MemberUseCase,
    HouseholdUseCase, AuthUseCase, CategoryUseCase
)
from app.application.interfaces import (
    AccountRepository, TransactionRepository, TransferRepository,
    LedgerEntryRepository, BudgetRepository, DebtRepository,
    DebtPaymentRepository, GoalRepository, GoalContributionRepository,
    AssetRepository, LiabilityRepository, MemberRepository,
    HouseholdRepository, CategoryRepository, RecurringPaymentRepository,
    NotificationRepository, UserRepository, SessionRepository
)


def get_repository() -> SQLiteRepository:
    return SQLiteRepository()


def get_transaction_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> TransactionUseCase:
    return TransactionUseCase(
        transaction_repo=repo,
        account_repo=repo,
        transfer_repo=repo,
        ledger_repo=repo,
    )


def get_budget_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> BudgetUseCase:
    return BudgetUseCase(repo)


def get_debt_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> DebtUseCase:
    return DebtUseCase(
        repo=repo,
        payment_repo=repo,
        account_repo=repo,
        ledger_repo=repo,
    )


def get_goal_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> GoalUseCase:
    return GoalUseCase(
        repo=repo,
        contribution_repo=repo,
        account_repo=repo,
        ledger_repo=repo,
    )


def get_account_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> AccountUseCase:
    return AccountUseCase(repo)


def get_asset_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> AssetUseCase:
    return AssetUseCase(repo)


def get_liability_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> LiabilityUseCase:
    return LiabilityUseCase(repo)


def get_member_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> MemberUseCase:
    return MemberUseCase(repo)


def get_household_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> HouseholdUseCase:
    return HouseholdUseCase(repo)


def get_category_use_case(
    repo: SQLiteRepository = Depends(get_repository),
):
    return CategoryUseCase(repo)


def get_auth_use_case(
    repo: SQLiteRepository = Depends(get_repository),
) -> AuthUseCase:
    return AuthUseCase(repo)


security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    repo: SQLiteRepository = Depends(get_repository),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    session_id = None
    if credentials and credentials.credentials:
        session_id = credentials.credentials
    else:
        session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = repo.get_session(session_id)
    if not session or not session.is_active:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = repo.get_user_by_id(session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")

    return {
        "user": user,
        "session": session,
    }


def get_household_id(current_user: dict = Depends(get_current_user)) -> str:
    return current_user["session"].household_id
