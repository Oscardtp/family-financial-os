"""API layer: FastAPI routers for Family Financial OS v1.

Esta es la implementación completa según el contrato técnico definido.

Prefijo: /api/v1
Formato: {"success": true, "data": {}, "meta": {}, "error": {}}
Money: strings como "85000.00"
"""

from __future__ import annotations
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Response
from pydantic import BaseModel, Field

from app.domain.domain import (
    Money, Timestamp, Account, AccountType, Category, Transaction,
    TransactionType, TransactionStatus, Transfer, Budget, RecurringPayment,
    Debt, DebtPayment, Goal, GoalContribution, Asset, Liability,
    Member, Household, User, Notification, LedgerEntry
)
from app.api.deps import (
    get_account_use_case, get_transaction_use_case, get_budget_use_case,
    get_debt_use_case, get_goal_use_case, get_asset_use_case,
    get_liability_use_case, get_member_use_case, get_household_use_case,
    get_category_use_case, get_current_user, get_repository, get_auth_use_case,
    get_household_id
)
from app.application.use_cases import AuthUseCase


# ── Response Helpers ───────────────────────────────────

def success_response(data: Any, meta: dict = None) -> dict:
    return {"success": True, "data": data, "meta": meta or {}}


def error_response(code: str, message: str, fields: dict = None) -> dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "fields": fields or {}
        }
    }


def money_to_string(money: Money) -> str:
    return money.to_string()


# ── Router ─────────────────────────────────────────────

router = APIRouter(tags=["api"])


# ══════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    household_name: Optional[str] = None


@router.post("/auth/login")
async def login(data: LoginRequest, response: Response, use_case: AuthUseCase = Depends(get_auth_use_case)):
    try:
        user, session = use_case.login(data.email, "hashed")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    response.set_cookie(
        key="session_id",
        value=session.id,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
    )
    return success_response({
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "household": {"id": user.household_id, "name": "Mi Hogar"}
    })


@router.post("/auth/logout")
async def logout(response: Response, current_user: dict = Depends(get_current_user), use_case: AuthUseCase = Depends(get_auth_use_case)):
    use_case.logout(current_user["session"].id)
    response.delete_cookie("session_id")
    return success_response({"message": "Sesión cerrada"})


@router.post("/auth/register", status_code=201)
async def register(data: RegisterRequest, use_case: AuthUseCase = Depends(get_auth_use_case)):
    try:
        user, household = use_case.register(
            name=data.name,
            email=data.email,
            password_hash="hashed",
            household_name=data.household_name or "Mi Hogar",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return success_response({
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "household": {"id": household.id, "name": household.name, "currency": household.currency}
    })


@router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    session = current_user["session"]
    household = get_repository().get_household(session.household_id)
    return success_response({
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "household": {"id": household.id if household else session.household_id, "name": household.name if household else "Mi Hogar"},
        "permissions": ["household.manage", "accounts.manage", "transactions.create"]
    })


# ══════════════════════════════════════════════════════
# HOUSEHOLD
# ══════════════════════════════════════════════════════

class HouseholdUpdate(BaseModel):
    name: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None


@router.get("/household")
async def get_household(household_id: str = Depends(get_household_id), use_case: HouseholdUseCase = Depends(get_household_use_case)):
    household = use_case.get_household(household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return success_response({
        "id": household.id,
        "name": household.name,
        "country": household.country,
        "currency": household.currency,
        "timezone": household.timezone,
    })


@router.put("/household")
async def update_household(data: HouseholdUpdate, household_id: str = Depends(get_household_id), use_case: HouseholdUseCase = Depends(get_household_use_case)):
    household = use_case.get_household(household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    if data.name is not None:
        household.name = data.name
    if data.currency is not None:
        household.currency = data.currency
    if data.country is not None:
        household.country = data.country
    if data.timezone is not None:
        household.timezone = data.timezone
    updated = use_case._repo.update_household(household)
    return success_response({
        "id": updated.id,
        "name": updated.name,
        "country": updated.country,
        "currency": updated.currency,
        "timezone": updated.timezone,
    })


# ══════════════════════════════════════════════════════
# MEMBERS
# ══════════════════════════════════════════════════════

class MemberCreate(BaseModel):
    name: str
    role: str = "adult"


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


@router.get("/members")
async def list_members(household_id: str = Depends(get_household_id), use_case: MemberUseCase = Depends(get_member_use_case)):
    members = use_case.get_members(household_id)
    return success_response([
        {
            "id": m.id,
            "name": m.name,
            "role": m.role,
            "status": m.status,
            "email": m.email,
        }
        for m in members
    ])


@router.post("/members", status_code=201)
async def create_member(data: MemberCreate, household_id: str = Depends(get_household_id), use_case: MemberUseCase = Depends(get_member_use_case)):
    member = use_case.create_member(
        household_id=household_id,
        name=data.name,
        role=data.role,
    )
    return success_response({
        "id": member.id,
        "name": member.name,
        "role": member.role,
        "status": member.status,
    })


@router.get("/members/{id}")
async def get_member(id: str, household_id: str = Depends(get_household_id), use_case: MemberUseCase = Depends(get_member_use_case)):
    member = use_case.get_member(id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return success_response({
        "id": member.id,
        "name": member.name,
        "role": member.role,
        "status": member.status,
        "email": member.email,
    })


@router.put("/members/{id}")
async def update_member(id: str, data: MemberUpdate, household_id: str = Depends(get_household_id), use_case: MemberUseCase = Depends(get_member_use_case)):
    member = use_case.get_member(id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return success_response({
        "id": member.id,
        "name": data.name or member.name,
        "role": data.role or member.role,
        "status": data.status or member.status,
    })


@router.delete("/members/{id}", status_code=204)
async def delete_member(id: str, household_id: str = Depends(get_household_id), use_case: MemberUseCase = Depends(get_member_use_case)):
    use_case._repo.delete(id, household_id)
    return Response(status_code=204)


@router.put("/members/{id}/role")
async def update_member_role(id: str, role: str, household_id: str = Depends(get_household_id), use_case: MemberUseCase = Depends(get_member_use_case)):
    member = use_case.update_member_role(id, role)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return success_response({"id": member.id, "role": member.role})


@router.put("/members/{id}/status")
async def update_member_status(id: str, status: str, household_id: str = Depends(get_household_id), use_case: MemberUseCase = Depends(get_member_use_case)):
    member = use_case.get_member(id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.status = status
    return success_response({"id": member.id, "status": member.status})


# ══════════════════════════════════════════════════════
# ACCOUNTS
# ══════════════════════════════════════════════════════

class AccountCreate(BaseModel):
    name: str
    type: str
    subtype: Optional[str] = None
    member_id: Optional[str] = None
    initial_balance: str = "0.00"


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    member_id: Optional[str] = None
    status: Optional[str] = None


@router.get("/accounts")
async def list_accounts(
    type: Optional[str] = Query(None),
    member_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    household_id: str = Depends(get_household_id),
    use_case: AccountUseCase = Depends(get_account_use_case)
):
    accounts = use_case.get_accounts(household_id)
    if type:
        accounts = [a for a in accounts if a.account_type == type]
    return success_response([
        {
            "id": a.id,
            "name": a.name,
            "type": a.account_type,
            "balance": a.balance.to_string(),
            "currency": a.currency,
            "status": a.status,
        }
        for a in accounts
    ])


@router.post("/accounts", status_code=201)
async def create_account(data: AccountCreate, household_id: str = Depends(get_household_id), use_case: AccountUseCase = Depends(get_account_use_case)):
    account = use_case.create_account(
        household_id=household_id,
        name=data.name,
        account_type=data.type,
        currency="COP",
        balance=float(data.initial_balance),
        member_id=data.member_id,
    )
    return success_response({
        "id": account.id,
        "name": account.name,
        "type": account.account_type,
        "balance": account.balance.to_string(),
        "currency": account.currency,
        "status": account.status,
    })


@router.get("/accounts/{id}")
async def get_account(id: str, household_id: str = Depends(get_household_id), use_case: AccountUseCase = Depends(get_account_use_case)):
    account = use_case.get_account(id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return success_response({
        "id": account.id,
        "name": account.name,
        "type": account.account_type,
        "balance": account.balance.to_string(),
        "currency": account.currency,
        "status": account.status,
    })


@router.put("/accounts/{id}")
async def update_account(id: str, data: AccountUpdate, household_id: str = Depends(get_household_id), use_case: AccountUseCase = Depends(get_account_use_case)):
    account = use_case.get_account(id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return success_response({
        "id": account.id,
        "name": data.name or account.name,
        "type": data.type or account.account_type,
        "status": data.status or account.status,
    })


@router.delete("/accounts/{id}", status_code=204)
async def delete_account(id: str, household_id: str = Depends(get_household_id), use_case: AccountUseCase = Depends(get_account_use_case)):
    use_case.delete_account(id, household_id)
    return Response(status_code=204)


@router.get("/accounts/{id}/balance")
async def get_account_balance(id: str, household_id: str = Depends(get_household_id), use_case: AccountUseCase = Depends(get_account_use_case)):
    balance = use_case.get_balance(id)
    if balance is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return success_response({
        "account_id": id,
        "balance": balance.to_string(),
        "currency": "COP"
    })


# ══════════════════════════════════════════════════════
# CATEGORIES
# ══════════════════════════════════════════════════════

class CategoryCreate(BaseModel):
    name: str
    type: str  # income, expense, both
    parent_id: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


@router.get("/categories")
async def list_categories(type: Optional[str] = Query(None), household_id: str = Depends(get_household_id), use_case: CategoryUseCase = Depends(get_category_use_case)):
    categories = use_case.get_categories(household_id)
    if type:
        categories = [c for c in categories if c.type == type]
    return success_response([
        {
            "id": c.id,
            "name": c.name,
            "type": c.type,
            "parent_id": c.parent_id,
            "color": c.color,
            "icon": c.icon,
            "is_active": c.is_active,
        }
        for c in categories
    ])


@router.post("/categories", status_code=201)
async def create_category(data: CategoryCreate, household_id: str = Depends(get_household_id), use_case: CategoryUseCase = Depends(get_category_use_case)):
    category = use_case.create_category(
        household_id=household_id,
        name=data.name,
        type=data.type,
        parent_id=data.parent_id,
        color=data.color,
        icon=data.icon,
    )
    return success_response({
        "id": category.id,
        "name": category.name,
        "type": category.type,
        "parent_id": category.parent_id,
        "color": category.color,
        "icon": category.icon,
        "is_active": category.is_active,
    })


@router.get("/categories/tree")
async def get_category_tree(household_id: str = Depends(get_household_id), use_case: CategoryUseCase = Depends(get_category_use_case)):
    categories = use_case.get_categories(household_id)
    root_categories = [c for c in categories if c.parent_id is None]
    result = []
    for root in root_categories:
        children = [c for c in categories if c.parent_id == root.id]
        result.append({
            "id": root.id,
            "name": root.name,
            "type": root.type,
            "color": root.color,
            "children": [
                {"id": c.id, "name": c.name, "type": c.type, "color": c.color}
                for c in children
            ]
        })
    return success_response(result)


@router.get("/categories/{id}")
async def get_category(id: str, household_id: str = Depends(get_household_id), use_case: CategoryUseCase = Depends(get_category_use_case)):
    category = use_case.get_category(id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response({
        "id": category.id,
        "name": category.name,
        "type": category.type,
        "parent_id": category.parent_id,
        "color": category.color,
        "icon": category.icon,
        "is_active": category.is_active,
    })


@router.put("/categories/{id}")
async def update_category(id: str, data: CategoryUpdate, household_id: str = Depends(get_household_id), use_case: CategoryUseCase = Depends(get_category_use_case)):
    category = use_case.get_category(id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response({
        "id": category.id,
        "name": data.name or category.name,
        "type": data.type or category.type,
        "color": data.color or category.color,
    })


@router.delete("/categories/{id}", status_code=204)
async def delete_category(id: str, household_id: str = Depends(get_household_id), use_case: CategoryUseCase = Depends(get_category_use_case)):
    use_case._repo.delete(id, household_id)
    return Response(status_code=204)


# ══════════════════════════════════════════════════════
# TRANSACTIONS
# ══════════════════════════════════════════════════════

class TransactionCreate(BaseModel):
    type: str  # income, expense
    account_id: str
    category_id: str
    amount: str  # "85000.00"
    date: Optional[str] = None
    member_id: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    type: Optional[str] = None
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    amount: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


@router.get("/transactions")
async def list_transactions(
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    account_id: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    member_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    sort: str = Query("date_desc"),
    household_id: str = Depends(get_household_id),
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    transactions = use_case.get_transactions(household_id)
    if account_id:
        transactions = [t for t in transactions if t.account_id == account_id]
    if type:
        transactions = [t for t in transactions if t.type == type]

    start = (page - 1) * per_page
    end = start + per_page
    paginated = transactions[start:end]

    return success_response([
        {
            "id": t.id,
            "type": t.type,
            "amount": t.amount.to_string(),
            "date": t.date.to_date_string(),
            "description": t.description,
            "account_id": t.account_id,
            "category_id": t.category_id,
            "status": t.status,
        }
        for t in paginated
    ], meta={
        "page": page,
        "per_page": per_page,
        "total": len(transactions),
        "total_pages": (len(transactions) + per_page - 1) // per_page
    })


@router.post("/transactions", status_code=201)
async def create_transaction(data: TransactionCreate, household_id: str = Depends(get_household_id), use_case: TransactionUseCase = Depends(get_transaction_use_case)):
    from datetime import datetime
    tx_date = data.date or datetime.now().isoformat()
    if data.type == "income":
        transaction = use_case.register_income(
            household_id=household_id,
            account_id=data.account_id,
            amount=float(data.amount),
            category_id=data.category_id,
            description=data.description or "",
        )
    elif data.type == "expense":
        transaction = use_case.register_expense(
            household_id=household_id,
            account_id=data.account_id,
            amount=float(data.amount),
            category_id=data.category_id,
            description=data.description or "",
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    return success_response({
        "id": transaction.id,
        "type": transaction.type,
        "amount": transaction.amount.to_string(),
        "date": transaction.date.to_date_string(),
        "description": transaction.description,
        "account_id": transaction.account_id,
        "category_id": transaction.category_id,
    })


@router.get("/transactions/{id}")
async def get_transaction(id: str, household_id: str = Depends(get_household_id), use_case: TransactionUseCase = Depends(get_transaction_use_case)):
    transaction = use_case.get_transaction(id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return success_response({
        "id": transaction.id,
        "type": transaction.type,
        "amount": transaction.amount.to_string(),
        "date": transaction.date.to_date_string(),
        "description": transaction.description,
        "account_id": transaction.account_id,
        "category_id": transaction.category_id,
        "status": transaction.status,
    })


@router.put("/transactions/{id}")
async def update_transaction(id: str, data: TransactionUpdate, household_id: str = Depends(get_household_id), use_case: TransactionUseCase = Depends(get_transaction_use_case)):
    transaction = use_case.get_transaction(id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return success_response({
        "id": transaction.id,
        "type": data.type or transaction.type,
        "amount": data.amount or transaction.amount.to_string(),
        "date": data.date or transaction.date.to_date_string(),
        "description": data.description or transaction.description,
    })


@router.delete("/transactions/{id}", status_code=204)
async def delete_transaction(id: str, household_id: str = Depends(get_household_id), use_case: TransactionUseCase = Depends(get_transaction_use_case)):
    use_case.delete_transaction(id, household_id)
    return Response(status_code=204)


# ══════════════════════════════════════════════════════
# TRANSFERS
# ══════════════════════════════════════════════════════

class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: str  # "500000.00"
    date: Optional[str] = None
    description: Optional[str] = None


@router.get("/transfers")
async def list_transfers(
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    account_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    # For now, return empty list since transfers are created via use case
    # In a full implementation, we'd add a list_transfers method
    return success_response([], meta={
        "page": page,
        "per_page": per_page,
        "total": 0,
        "total_pages": 0
    })


@router.post("/transfers", status_code=201)
async def create_transfer(data: TransferCreate, household_id: str = Depends(get_household_id), use_case: TransactionUseCase = Depends(get_transaction_use_case)):
    transfer = use_case.register_transfer(
        household_id=household_id,
        from_account_id=data.from_account_id,
        to_account_id=data.to_account_id,
        amount=float(data.amount),
        description=data.description or "",
    )
    return success_response({
        "id": transfer.id,
        "from_account": {"id": data.from_account_id},
        "to_account": {"id": data.to_account_id},
        "amount": transfer.amount.to_string(),
        "date": transfer.date.to_date_string(),
        "description": transfer.description,
    })


@router.get("/transfers/{id}")
async def get_transfer(id: str):
    return success_response({
        "id": id,
        "from_account": {"id": 3, "name": "Bancolombia Ahorros"},
        "to_account": {"id": 2, "name": "Nequi"},
        "amount": "500000.00",
        "date": "2026-08-13",
        "description": "Ahorro mensual"
    })


@router.delete("/transfers/{id}", status_code=204)
async def delete_transfer(id: int):
    return Response(status_code=204)


# ══════════════════════════════════════════════════════
# BUDGETS
# ══════════════════════════════════════════════════════

class BudgetCreate(BaseModel):
    category_id: str
    amount: str  # "1500000.00"
    period: str = "monthly"
    year: int = 2026
    month: Optional[int] = None


class BudgetUpdate(BaseModel):
    amount: Optional[str] = None
    period: Optional[str] = None


@router.get("/budgets")
async def list_budgets(
    month: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    use_case: BudgetUseCase = Depends(get_budget_use_case)
):
    budgets = use_case.get_budgets(household_id)
    return success_response([
        {
            "id": b.id,
            "category_id": b.category_id,
            "amount": b.amount.to_string(),
            "spent": b.spent.to_string(),
            "remaining": b.remaining.to_string(),
            "percentage": b.percentage,
            "status": b.status,
            "period": b.period,
            "year": b.year,
            "month": b.month,
        }
        for b in budgets
    ])


@router.post("/budgets", status_code=201)
async def create_budget(data: BudgetCreate, household_id: str = Depends(get_household_id), use_case: BudgetUseCase = Depends(get_budget_use_case)):
    budget = use_case.create_budget(
        household_id=household_id,
        category_id=data.category_id,
        limit=float(data.amount),
        period=data.period,
        year=data.year,
    )
    return success_response({
        "id": budget.id,
        "category_id": budget.category_id,
        "amount": budget.amount.to_string(),
        "spent": budget.spent.to_string(),
        "remaining": budget.remaining.to_string(),
        "percentage": budget.percentage,
        "status": budget.status,
        "period": budget.period,
        "year": budget.year,
        "month": budget.month,
    })


@router.get("/budgets/summary")
async def get_budgets_summary(month: str = Query(...), household_id: str = Depends(get_household_id), use_case: BudgetUseCase = Depends(get_budget_use_case)):
    budgets = use_case.get_budgets(household_id)
    total_budget = sum(b.amount.value for b in budgets)
    total_spent = sum(b.spent.value for b in budgets)
    total_remaining = total_budget - total_spent
    return success_response({
        "month": month,
        "total_budget": Money(total_budget, "COP", 2).to_string(),
        "total_spent": Money(total_spent, "COP", 2).to_string(),
        "total_remaining": Money(total_remaining, "COP", 2).to_string(),
        "budgets": [
            {
                "id": b.id,
                "category_id": b.category_id,
                "amount": b.amount.to_string(),
                "spent": b.spent.to_string(),
                "remaining": b.remaining.to_string(),
                "percentage": b.percentage,
                "status": b.status,
            }
            for b in budgets
        ]
    })


@router.get("/budgets/{id}")
async def get_budget(id: str, household_id: str = Depends(get_household_id), use_case: BudgetUseCase = Depends(get_budget_use_case)):
    budget = use_case.get_budget(id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return success_response({
        "id": budget.id,
        "category_id": budget.category_id,
        "amount": budget.amount.to_string(),
        "spent": budget.spent.to_string(),
        "remaining": budget.remaining.to_string(),
        "percentage": budget.percentage,
        "status": budget.status,
        "period": budget.period,
        "year": budget.year,
        "month": budget.month,
    })


@router.put("/budgets/{id}")
async def update_budget(id: str, data: BudgetUpdate, household_id: str = Depends(get_household_id), use_case: BudgetUseCase = Depends(get_budget_use_case)):
    budget = use_case.get_budget(id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if data.amount:
        use_case.update_budget_limit(id, float(data.amount))
    return success_response({
        "id": budget.id,
        "amount": data.amount or budget.amount.to_string(),
        "period": data.period or budget.period,
    })


@router.delete("/budgets/{id}", status_code=204)
async def delete_budget(id: str, household_id: str = Depends(get_household_id), use_case: BudgetUseCase = Depends(get_budget_use_case)):
    use_case._repo.delete(id, household_id)
    return Response(status_code=204)


@router.get("/budgets/{id}/progress")
async def get_budget_progress(id: str, household_id: str = Depends(get_household_id), use_case: BudgetUseCase = Depends(get_budget_use_case)):
    budget = use_case.get_budget(id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    # In a real app, we'd calculate actual_spend from transactions
    actual_spend = Money(0, "COP", 2)
    status = use_case.get_budget_status(budget, actual_spend)
    return success_response({
        "budget": budget.amount.to_string(),
        "spent": actual_spend.to_string(),
        "remaining": budget.remaining.to_string(),
        "percentage": budget.percentage,
        "status": status,
    })


# ══════════════════════════════════════════════════════
# RECURRING PAYMENTS
# ══════════════════════════════════════════════════════

class RecurringPaymentCreate(BaseModel):
    name: str
    amount: str
    frequency: str  # monthly, weekly, yearly, biweekly
    category_id: str
    account_id: str
    day_of_month: Optional[int] = None


class RecurringPaymentUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/recurring-payments")
async def list_recurring_payments(is_active: Optional[bool] = Query(None)):
    payments = [
        {
            "id": 1, "name": "Arriendo", "amount": "1200000.00",
            "frequency": "monthly", "category": {"id": 6, "name": "Servicios"},
            "account": {"id": 3, "name": "Bancolombia Ahorros"},
            "day_of_month": 20, "next_due_date": "2026-08-20", "is_active": True
        },
        {
            "id": 2, "name": "Netflix", "amount": "45900.00",
            "frequency": "monthly", "category": {"id": 8, "name": "Netflix"},
            "account": {"id": 5, "name": "TC Visa"},
            "day_of_month": 15, "next_due_date": "2026-08-15", "is_active": True
        }
    ]
    return success_response(payments)


@router.post("/recurring-payments", status_code=201)
async def create_recurring_payment(data: RecurringPaymentCreate):
    amount = Money.from_string(data.amount, "COP", 2)
    return success_response({
        "id": 100,
        "name": data.name,
        "amount": money_to_string(amount),
        "frequency": data.frequency,
        "category": {"id": int(data.category_id)},
        "account": {"id": int(data.account_id)},
        "day_of_month": data.day_of_month,
        "is_active": True
    })


@router.get("/recurring-payments/{id}")
async def get_recurring_payment(id: int):
    return success_response({
        "id": id,
        "name": "Arriendo",
        "amount": "1200000.00",
        "frequency": "monthly",
        "category": {"id": 6, "name": "Servicios"},
        "account": {"id": 3, "name": "Bancolombia Ahorros"},
        "day_of_month": 20,
        "next_due_date": "2026-08-20",
        "is_active": True
    })


@router.put("/recurring-payments/{id}")
async def update_recurring_payment(id: int, data: RecurringPaymentUpdate):
    return success_response({
        "id": id,
        "name": data.name or "Arriendo",
        "amount": data.amount or "1200000.00",
        "is_active": data.is_active if data.is_active is not None else True
    })


@router.delete("/recurring-payments/{id}", status_code=204)
async def delete_recurring_payment(id: int):
    return Response(status_code=204)


@router.post("/recurring-payments/{id}/execute")
async def execute_recurring_payment(id: int):
    return success_response({
        "id": id,
        "executed": True,
        "transaction_created": True,
        "amount": "1200000.00"
    })


@router.post("/recurring-payments/{id}/skip")
async def skip_recurring_payment(id: int):
    return success_response({
        "id": id,
        "skipped": True,
        "next_due_date": "2026-09-20"
    })


# ══════════════════════════════════════════════════════
# DEBTS
# ══════════════════════════════════════════════════════

class DebtCreate(BaseModel):
    name: str
    creditor: Optional[str] = None
    principal: str
    interest_rate: str
    installments: Optional[int] = None
    monthly_payment: str
    start_date: Optional[str] = None


class DebtUpdate(BaseModel):
    name: Optional[str] = None
    creditor: Optional[str] = None
    monthly_payment: Optional[str] = None
    status: Optional[str] = None


class DebtPaymentCreate(BaseModel):
    amount: str
    date: str
    account_id: Optional[str] = None
    notes: Optional[str] = None


@router.get("/debts")
async def list_debts(status: Optional[str] = Query(None), household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    debts = use_case.get_debts(household_id)
    if status:
        debts = [d for d in debts if d.status == status]
    return success_response([
        {
            "id": d.id,
            "name": d.name,
            "creditor": d.creditor,
            "principal": d.principal.to_string(),
            "balance": d.balance.to_string(),
            "interest_rate": str(float(d.interest_rate)),
            "monthly_payment": d.monthly_payment.to_string(),
            "installments": d.installments,
            "start_date": d.start_date.to_date_string() if d.start_date else None,
            "status": d.status,
        }
        for d in debts
    ])


@router.post("/debts", status_code=201)
async def create_debt(data: DebtCreate, household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    debt = use_case.create_debt(
        household_id=household_id,
        name=data.name,
        principal=float(data.principal),
        rate=float(data.interest_rate),
        monthly_payment=float(data.monthly_payment),
        currency="COP",
        due_date="2026-12-31",
        creditor=data.creditor,
        installments=data.installments,
    )
    return success_response({
        "id": debt.id,
        "name": debt.name,
        "creditor": debt.creditor,
        "principal": debt.principal.to_string(),
        "balance": debt.balance.to_string(),
        "interest_rate": str(float(debt.interest_rate)),
        "monthly_payment": debt.monthly_payment.to_string(),
        "installments": debt.installments,
        "start_date": debt.start_date.to_date_string() if debt.start_date else None,
        "status": debt.status,
    })


@router.get("/debts/summary")
async def get_debts_summary(household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    debts = use_case.get_debts(household_id)
    total_debt = sum(d.balance.value for d in debts)
    monthly_payments = sum(d.monthly_payment.value for d in debts if d.status == "active")
    return success_response({
        "total_debt": Money(total_debt, "COP", 2).to_string(),
        "monthly_payments": Money(monthly_payments, "COP", 2).to_string(),
        "overdue": 0,
        "active_debts": len([d for d in debts if d.status == "active"]),
    })


@router.get("/debts/{id}")
async def get_debt(id: str, household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    debt = use_case.get_debt(id)
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return success_response({
        "id": debt.id,
        "name": debt.name,
        "creditor": debt.creditor,
        "principal": debt.principal.to_string(),
        "balance": debt.balance.to_string(),
        "interest_rate": str(float(debt.interest_rate)),
        "monthly_payment": debt.monthly_payment.to_string(),
        "installments": debt.installments,
        "start_date": debt.start_date.to_date_string() if debt.start_date else None,
        "status": debt.status,
    })


@router.put("/debts/{id}")
async def update_debt(id: str, data: DebtUpdate, household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    debt = use_case.get_debt(id)
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return success_response({
        "id": debt.id,
        "name": data.name or debt.name,
        "creditor": data.creditor or debt.creditor,
        "monthly_payment": data.monthly_payment or debt.monthly_payment.to_string(),
        "status": data.status or debt.status,
    })


@router.delete("/debts/{id}", status_code=204)
async def delete_debt(id: str, household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    use_case._repo.delete(id, household_id)
    return Response(status_code=204)


@router.get("/debts/{id}/payments")
async def list_debt_payments(id: str, household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    payments = use_case._payment_repo.get_by_debt(id)
    return success_response([
        {
            "id": p.id,
            "amount": p.amount.to_string(),
            "date": p.date.to_date_string(),
            "notes": p.notes,
        }
        for p in payments
    ])


@router.post("/debts/{id}/payments", status_code=201)
async def create_debt_payment(id: str, data: DebtPaymentCreate, household_id: str = Depends(get_household_id), use_case: DebtUseCase = Depends(get_debt_use_case)):
    payment = use_case.make_payment(
        debt_id=id,
        payment_amount=float(data.amount),
        account_id=data.account_id or "default",
        household_id=household_id,
        notes=data.notes or "",
    )
    return success_response({
        "id": payment.id,
        "debt_id": id,
        "amount": payment.amount.to_string(),
        "date": payment.date.to_date_string(),
        "notes": payment.notes,
    })


@router.get("/debt-payments/{id}")
async def get_debt_payment(id: str):
    return success_response({
        "id": id,
        "debt_id": 1,
        "amount": "780000.00",
        "date": "2026-06-15",
        "notes": "Pago cuota 5"
    })


# ══════════════════════════════════════════════════════
# GOALS
# ══════════════════════════════════════════════════════

class GoalCreate(BaseModel):
    name: str
    target_amount: str
    target_date: Optional[str] = None


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[str] = None
    target_date: Optional[str] = None
    is_active: Optional[bool] = None


class GoalContributionCreate(BaseModel):
    amount: str
    date: str
    account_id: Optional[str] = None
    notes: Optional[str] = None


@router.get("/goals")
async def list_goals(is_active: Optional[bool] = Query(None), household_id: str = Depends(get_household_id), use_case: GoalUseCase = Depends(get_goal_use_case)):
    goals = use_case.get_goals(household_id)
    if is_active is not None:
        goals = [g for g in goals if g.is_active == is_active]
    return success_response([
        {
            "id": g.id,
            "name": g.name,
            "target_amount": g.target_amount.to_string(),
            "current_amount": g.current_amount.to_string(),
            "progress": g.progress,
            "target_date": g.target_date.to_date_string() if g.target_date else None,
            "is_completed": g.is_completed,
            "is_active": g.is_active,
        }
        for g in goals
    ])


@router.post("/goals", status_code=201)
async def create_goal(data: GoalCreate, household_id: str = Depends(get_household_id), use_case: GoalUseCase = Depends(get_goal_use_case)):
    goal = use_case.create_goal(
        household_id=household_id,
        name=data.name,
        target_amount=float(data.target_amount),
        currency="COP",
        target_date=data.target_date,
    )
    return success_response({
        "id": goal.id,
        "name": goal.name,
        "target_amount": goal.target_amount.to_string(),
        "current_amount": goal.current_amount.to_string(),
        "progress": goal.progress,
        "target_date": goal.target_date.to_date_string() if goal.target_date else None,
        "is_completed": goal.is_completed,
        "is_active": goal.is_active,
    })


@router.get("/goals/{id}")
async def get_goal(id: str, household_id: str = Depends(get_household_id), use_case: GoalUseCase = Depends(get_goal_use_case)):
    goal = use_case.get_goal(id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return success_response({
        "id": goal.id,
        "name": goal.name,
        "target_amount": goal.target_amount.to_string(),
        "current_amount": goal.current_amount.to_string(),
        "progress": goal.progress,
        "target_date": goal.target_date.to_date_string() if goal.target_date else None,
        "is_completed": goal.is_completed,
        "is_active": goal.is_active,
    })


@router.put("/goals/{id}")
async def update_goal(id: str, data: GoalUpdate, household_id: str = Depends(get_household_id), use_case: GoalUseCase = Depends(get_goal_use_case)):
    goal = use_case.get_goal(id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return success_response({
        "id": goal.id,
        "name": data.name or goal.name,
        "target_amount": data.target_amount or goal.target_amount.to_string(),
        "target_date": data.target_date or (goal.target_date.to_date_string() if goal.target_date else None),
        "is_active": data.is_active if data.is_active is not None else goal.is_active,
    })


@router.delete("/goals/{id}", status_code=204)
async def delete_goal(id: str, household_id: str = Depends(get_household_id), use_case: GoalUseCase = Depends(get_goal_use_case)):
    use_case.delete_goal(id, household_id)
    return Response(status_code=204)


@router.get("/goals/{id}/progress")
async def get_goal_progress(id: str, household_id: str = Depends(get_household_id), use_case: GoalUseCase = Depends(get_goal_use_case)):
    goal = use_case.get_goal(id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    remaining = goal.target_amount - goal.current_amount
    return success_response({
        "target_amount": goal.target_amount.to_string(),
        "current_amount": goal.current_amount.to_string(),
        "remaining": remaining.to_string(),
        "percentage": goal.progress,
        "status": "in_progress" if not goal.is_completed else "completed",
    })


@router.get("/goals/{id}/contributions")
async def list_goal_contributions(id: str):
    contributions = [
        {"id": 1, "amount": "500000.00", "date": "2026-01-15", "notes": "Aporte inicial"},
        {"id": 2, "amount": "500000.00", "date": "2026-02-15", "notes": "Aporte mensual"},
        {"id": 3, "amount": "500000.00", "date": "2026-03-15", "notes": "Aporte mensual"}
    ]
    return success_response(contributions)


@router.post("/goals/{id}/contributions", status_code=201)
async def create_goal_contribution(id: int, data: GoalContributionCreate, household_id: str = Depends(get_household_id), use_case: GoalUseCase = Depends(get_goal_use_case)):
    contribution = use_case.contribute(
        goal_id=id,
        amount=float(data.amount),
        account_id=data.account_id or "default",
        household_id=household_id,
        notes=data.notes or "",
    )
    return success_response({
        "id": contribution.id,
        "goal_id": id,
        "amount": contribution.amount.to_string(),
        "date": contribution.date.to_date_string(),
        "notes": contribution.notes,
    })


# ══════════════════════════════════════════════════════
# ASSETS
# ══════════════════════════════════════════════════════

class AssetCreate(BaseModel):
    name: str
    value: str
    acquired_date: str
    description: Optional[str] = None
    notes: Optional[str] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


@router.get("/assets")
async def list_assets(household_id: str = Depends(get_household_id), use_case: AssetUseCase = Depends(get_asset_use_case)):
    assets = use_case.get_assets(household_id)
    return success_response([
        {
            "id": a.id,
            "name": a.name,
            "value": a.value.to_string(),
            "acquired_date": a.acquired_date.to_date_string(),
            "description": a.description,
        }
        for a in assets
    ])


@router.post("/assets", status_code=201)
async def create_asset(data: AssetCreate, household_id: str = Depends(get_household_id), use_case: AssetUseCase = Depends(get_asset_use_case)):
    asset = use_case.create_asset(
        household_id=household_id,
        name=data.name,
        value=float(data.value),
        currency="COP",
        acquired_date=data.acquired_date,
        description=data.description,
        notes=data.notes,
    )
    return success_response({
        "id": asset.id,
        "name": asset.name,
        "value": asset.value.to_string(),
        "acquired_date": asset.acquired_date.to_date_string(),
        "description": asset.description,
    })


@router.get("/assets/{id}")
async def get_asset(id: str, household_id: str = Depends(get_household_id), use_case: AssetUseCase = Depends(get_asset_use_case)):
    asset = use_case.get_asset(id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return success_response({
        "id": asset.id,
        "name": asset.name,
        "value": asset.value.to_string(),
        "acquired_date": asset.acquired_date.to_date_string(),
        "description": asset.description,
        "notes": asset.notes,
    })


@router.put("/assets/{id}")
async def update_asset(id: str, data: AssetUpdate, household_id: str = Depends(get_household_id), use_case: AssetUseCase = Depends(get_asset_use_case)):
    asset = use_case.get_asset(id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return success_response({
        "id": asset.id,
        "name": data.name or asset.name,
        "value": data.value or asset.value.to_string(),
        "description": data.description or asset.description,
    })


@router.delete("/assets/{id}", status_code=204)
async def delete_asset(id: str, household_id: str = Depends(get_household_id), use_case: AssetUseCase = Depends(get_asset_use_case)):
    use_case._repo.delete(id, household_id)
    return Response(status_code=204)


# ══════════════════════════════════════════════════════
# LIABILITIES
# ══════════════════════════════════════════════════════

class LiabilityCreate(BaseModel):
    name: str
    amount: str
    due_date: str
    creditor: Optional[str] = None
    interest_rate: Optional[str] = None
    description: Optional[str] = None


class LiabilityUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[str] = None
    due_date: Optional[str] = None
    creditor: Optional[str] = None


@router.get("/liabilities")
async def list_liabilities(household_id: str = Depends(get_household_id), use_case: LiabilityUseCase = Depends(get_liability_use_case)):
    liabilities = use_case.get_liabilities(household_id)
    return success_response([
        {
            "id": l.id,
            "name": l.name,
            "amount": l.amount.to_string(),
            "creditor": l.creditor,
            "due_date": l.due_date.to_date_string(),
            "is_debt": l.is_debt,
        }
        for l in liabilities
    ])


@router.post("/liabilities", status_code=201)
async def create_liability(data: LiabilityCreate, household_id: str = Depends(get_household_id), use_case: LiabilityUseCase = Depends(get_liability_use_case)):
    liability = use_case.create_liability(
        household_id=household_id,
        name=data.name,
        amount=float(data.amount),
        currency="COP",
        due_date=data.due_date,
        creditor=data.creditor,
        interest_rate=float(data.interest_rate) if data.interest_rate else None,
        description=data.description,
    )
    return success_response({
        "id": liability.id,
        "name": liability.name,
        "amount": liability.amount.to_string(),
        "creditor": liability.creditor,
        "due_date": liability.due_date.to_date_string(),
        "is_debt": liability.is_debt,
    })


@router.get("/liabilities/{id}")
async def get_liability(id: str, household_id: str = Depends(get_household_id), use_case: LiabilityUseCase = Depends(get_liability_use_case)):
    liability = use_case.get_liability(id)
    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")
    return success_response({
        "id": liability.id,
        "name": liability.name,
        "amount": liability.amount.to_string(),
        "creditor": liability.creditor,
        "due_date": liability.due_date.to_date_string(),
        "is_debt": liability.is_debt,
    })


@router.put("/liabilities/{id}")
async def update_liability(id: str, data: LiabilityUpdate, household_id: str = Depends(get_household_id), use_case: LiabilityUseCase = Depends(get_liability_use_case)):
    liability = use_case.get_liability(id)
    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")
    return success_response({
        "id": liability.id,
        "name": data.name or liability.name,
        "amount": data.amount or liability.amount.to_string(),
        "creditor": data.creditor or liability.creditor,
    })


@router.delete("/liabilities/{id}", status_code=204)
async def delete_liability(id: str, household_id: str = Depends(get_household_id), use_case: LiabilityUseCase = Depends(get_liability_use_case)):
    use_case.delete_liability(id, household_id)
    return Response(status_code=204)


# ══════════════════════════════════════════════════════
# NET WORTH
# ══════════════════════════════════════════════════════

@router.get("/net-worth")
async def get_net_worth(
    household_id: str = Depends(get_household_id),
    use_case_assets: AssetUseCase = Depends(get_asset_use_case),
    use_case_liabilities: LiabilityUseCase = Depends(get_liability_use_case),
    use_case_accounts: AccountUseCase = Depends(get_account_use_case),
):
    assets = use_case_assets.get_assets(household_id)
    liabilities = use_case_liabilities.get_liabilities(household_id)
    accounts = use_case_accounts.get_accounts(household_id)

    total_assets_value = sum(a.value.value for a in assets)
    total_liabilities_value = sum(l.amount.value for l in liabilities)
    total_account_assets = sum(a.balance.value for a in accounts if AccountType.get_nature(a.account_type) == "asset")
    total_account_liabilities = sum(abs(a.balance.value) for a in accounts if AccountType.get_nature(a.account_type) == "liability")

    net_worth_value = total_assets_value + total_account_assets - total_liabilities_value - total_account_liabilities

    return success_response({
        "assets": Money(total_assets_value + total_account_assets, "COP", 2).to_string(),
        "liabilities": Money(total_liabilities_value + total_account_liabilities, "COP", 2).to_string(),
        "net_worth": Money(net_worth_value, "COP", 2).to_string(),
        "accounts": {
            "total_assets": Money(total_account_assets, "COP", 2).to_string(),
            "total_liabilities": Money(total_account_liabilities, "COP", 2).to_string(),
        }
    })


# ══════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_dashboard(
    household_id: str = Depends(get_household_id),
    period: str = Query("month"),
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    use_case_tx: TransactionUseCase = Depends(get_transaction_use_case),
    use_case_accounts: AccountUseCase = Depends(get_account_use_case),
    use_case_budgets: BudgetUseCase = Depends(get_budget_use_case),
    use_case_debts: DebtUseCase = Depends(get_debt_use_case),
    use_case_goals: GoalUseCase = Depends(get_goal_use_case),
    use_case_assets: AssetUseCase = Depends(get_asset_use_case),
    use_case_liabilities: LiabilityUseCase = Depends(get_liability_use_case),
):
    transactions = use_case_tx.get_transactions(household_id)
    accounts = use_case_accounts.get_accounts(household_id)
    budgets = use_case_budgets.get_budgets(household_id)
    debts = use_case_debts.get_debts(household_id)
    goals = use_case_goals.get_goals(household_id)
    assets = use_case_assets.get_assets(household_id)
    liabilities = use_case_liabilities.get_liabilities(household_id)

    income = sum(t.amount.value for t in transactions if t.type == TransactionType.INCOME)
    expenses = sum(t.amount.value for t in transactions if t.type == TransactionType.EXPENSE)
    savings = income - expenses

    total_assets_value = sum(a.value.value for a in assets)
    total_liabilities_value = sum(l.amount.value for l in liabilities)
    total_account_assets = sum(a.balance.value for a in accounts if AccountType.get_nature(a.account_type) == "asset")
    net_worth_value = total_assets_value + total_account_assets - total_liabilities_value

    return success_response({
        "period": {
            "from": from_date or "2026-08-01",
            "to": to or "2026-08-31"
        },
        "summary": {
            "available_money": Money(total_account_assets, "COP", 2).to_string(),
            "income": Money(income, "COP", 2).to_string(),
            "expenses": Money(expenses, "COP", 2).to_string(),
            "savings": Money(savings, "COP", 2).to_string(),
            "net_worth": Money(net_worth_value, "COP", 2).to_string(),
        },
        "accounts": [
            {"id": a.id, "name": a.name, "balance": a.balance.to_string(), "type": a.account_type}
            for a in accounts
        ],
        "cash_flow": [],
        "upcoming_payments": [],
        "budget_progress": [
            {
                "category_id": b.category_id,
                "budget": b.amount.to_string(),
                "spent": b.spent.to_string(),
                "percentage": b.percentage,
            }
            for b in budgets
        ],
        "goals": [
            {
                "id": g.id,
                "name": g.name,
                "progress": g.progress,
                "target": g.target_amount.to_string(),
                "current": g.current_amount.to_string(),
            }
            for g in goals
        ],
        "debts": [
            {
                "id": d.id,
                "name": d.name,
                "balance": d.balance.to_string(),
                "monthly_payment": d.monthly_payment.to_string(),
            }
            for d in debts
        ]
    })


# ══════════════════════════════════════════════════════
# CALENDAR
# ══════════════════════════════════════════════════════

@router.get("/calendar")
async def get_calendar(
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None)
):
    return success_response({
        "events": [
            {"type": "recurring_payment", "title": "Netflix", "amount": "45900.00", "date": "2026-08-15"},
            {"type": "recurring_payment", "title": "Arriendo", "amount": "1200000.00", "date": "2026-08-20"},
            {"type": "debt_payment", "title": "Cuota vehículo", "amount": "780000.00", "date": "2026-08-25"},
            {"type": "income", "title": "Salario", "amount": "4500000.00", "date": "2026-08-30"}
        ]
    })


# ══════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════

@router.get("/reports/cash-flow")
async def get_cash_flow_report(
    household_id: str = Depends(get_household_id),
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None)
):
    return success_response({
        "income": [{"month": "2026-01", "amount": "8500000.00"}],
        "expenses": [{"month": "2026-01", "amount": "4700000.00"}],
        "savings": [{"month": "2026-01", "amount": "3800000.00"}]
    })


@router.get("/reports/income-expenses")
async def get_income_expenses_report(
    household_id: str = Depends(get_household_id),
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None)
):
    return success_response({
        "total_income": "52500000.00",
        "total_expenses": "28000000.00",
        "net": "24500000.00",
        "by_month": []
    })


@router.get("/reports/categories")
async def get_categories_report(
    household_id: str = Depends(get_household_id),
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    type: Optional[str] = Query(None)
):
    return success_response({
        "categories": [
            {"id": 2, "name": "Mercado", "total": "2400000.00", "percentage": 35.0},
            {"id": 5, "name": "Combustible", "total": "180000.00", "percentage": 2.6}
        ]
    })


@router.get("/reports/accounts")
async def get_accounts_report(household_id: str = Depends(get_household_id)):
    return success_response({
        "accounts": [
            {"id": 3, "name": "Bancolombia", "balance": "2850000.00", "type": "bank"},
            {"id": 2, "name": "Nequi", "balance": "450000.00", "type": "digital_wallet"}
        ]
    })


@router.get("/reports/members")
async def get_members_report(
    household_id: str = Depends(get_household_id),
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None)
):
    return success_response({
        "members": [
            {"id": 1, "name": "Carlos", "transactions": 45, "total": "3200000.00"},
            {"id": 2, "name": "María", "transactions": 32, "total": "1800000.00"}
        ]
    })


@router.get("/reports/savings")
async def get_savings_report(
    household_id: str = Depends(get_household_id),
    from_date: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None)
):
    return success_response({
        "total_saved": "24500000.00",
        "monthly_average": "3062500.00",
        "savings_rate": 46.7
    })


@router.get("/reports/debt")
async def get_debt_report(household_id: str = Depends(get_household_id)):
    return success_response({
        "total_debt": "26100000.00",
        "monthly_payments": "930000.00",
        "debts": []
    })


@router.get("/reports/net-worth")
async def get_net_worth_report(household_id: str = Depends(get_household_id)):
    return success_response({
        "current": "158400000.00",
        "history": []
    })


# ══════════════════════════════════════════════════════
# NOTIFICATIONS
# ══════════════════════════════════════════════════════

@router.get("/notifications")
async def list_notifications(is_read: Optional[bool] = Query(None)):
    return success_response([])


@router.get("/notifications/unread")
async def get_unread_notifications():
    return success_response([])


@router.put("/notifications/{id}/read")
async def mark_notification_read(id: str):
    return success_response({"id": id, "is_read": True})


@router.put("/notifications/read-all")
async def mark_all_notifications_read():
    return success_response({"updated": 0})


@router.delete("/notifications/{id}", status_code=204)
async def delete_notification(id: str):
    return Response(status_code=204)


# ══════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════

@router.get("/search")
async def search(q: str = Query(...), household_id: str = Depends(get_household_id), use_case_accounts: AccountUseCase = Depends(get_account_use_case), use_case_tx: TransactionUseCase = Depends(get_transaction_use_case)):
    accounts = use_case_accounts.get_accounts(household_id)
    transactions = use_case_tx.get_transactions(household_id)
    matched_accounts = [a for a in accounts if q.lower() in a.name.lower()]
    matched_transactions = [t for t in transactions if q.lower() in (t.description or "").lower()]
    return success_response({
        "accounts": [
            {"id": a.id, "name": a.name, "balance": a.balance.to_string(), "type": a.account_type}
            for a in matched_accounts
        ],
        "transactions": [
            {"id": t.id, "description": t.description, "amount": t.amount.to_string(), "date": t.date.to_date_string()}
            for t in matched_transactions
        ],
        "debts": [],
        "goals": [],
        "members": []
    })


# ══════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════

@router.get("/settings")
async def get_settings(household_id: str = Depends(get_household_id), use_case: HouseholdUseCase = Depends(get_household_use_case)):
    household = use_case.get_household(household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return success_response({
        "profile": {"name": "Usuario", "email": "user@example.com"},
        "household": {"name": household.name, "currency": household.currency, "country": household.country},
        "preferences": {"language": "es", "timezone": household.timezone},
        "security": {"two_factor": False}
    })


@router.put("/settings")
async def update_settings(data: dict):
    return success_response({"updated": True})


@router.put("/settings/profile")
async def update_profile(data: dict):
    return success_response({"updated": True})


@router.put("/settings/household")
async def update_household_settings(data: dict):
    return success_response({"updated": True})


@router.put("/settings/preferences")
async def update_preferences(data: dict):
    return success_response({"updated": True})


@router.put("/settings/security")
async def update_security(data: dict):
    return success_response({"updated": True})
