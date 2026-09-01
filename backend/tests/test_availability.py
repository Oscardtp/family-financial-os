import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import test_session_factory
from app.infrastructure.models.models import (
    HouseholdModel,
    UserModel,
    AccountModel,
    FinancialEventModel,
    CategoryModel,
    BudgetModel,
    TransactionModel,
)
from app.application.services.calendar_service import CalendarService
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_service(db: AsyncSession) -> CalendarService:
    return CalendarService(
        db,
        account_repo=SQLAlchemyAccountRepository(db),
        event_repo=SQLAlchemyFinancialEventRepository(db),
        budget_repo=SQLAlchemyBudgetRepository(db),
        tx_repo=SQLAlchemyTransactionRepository(db),
    )


@pytest.mark.anyio
async def test_availability_seven_days(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "avail@example.com",
        "name": "Avail User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Bancolombia", "type": "bank", "balance": 2000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    cash = await client.post(
        "/api/v1/accounts",
        json={"name": "Efectivo", "type": "cash", "balance": 200000},
        headers=headers,
    )
    cash_id = cash.json()["id"]

    today = date.today()
    for i in range(3):
        d = today + timedelta(days=i + 1)
        await client.post(
            "/api/v1/events",
            json={
                "title": f"Gasto {i}",
                "type": "expense",
                "amount": 150000,
                "due_date": d.isoformat(),
                "account_id": account_id,
                "payment_method": "card",
                "status": "pending",
            },
            headers=headers,
        )

    await client.post(
        "/api/v1/events",
        json={
            "title": "Salario",
            "type": "income",
            "amount": 3000000,
            "due_date": (today + timedelta(days=2)).isoformat(),
            "status": "pending",
        },
        headers=headers,
    )

    resp = await client.get("/api/v1/events/availability", params={"days": 7}, headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["days"] == 7
    assert body["available"] == 2200000
    assert body["upcoming_payments"] == 450000
    assert body["projected_available"] == 1750000
    assert body["expected_income"] == 3000000
    assert body["expected_expenses"] == 450000


@pytest.mark.anyio
async def test_availability_cash_needed(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "cash@example.com",
        "name": "Cash User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    await client.post(
        "/api/v1/accounts",
        json={"name": "Bancolombia", "type": "bank", "balance": 1000000},
        headers=headers,
    )

    cash = await client.post(
        "/api/v1/accounts",
        json={"name": "Efectivo", "type": "cash", "balance": 50000},
        headers=headers,
    )
    cash_id = cash.json()["id"]

    today = date.today()
    await client.post(
        "/api/v1/events",
        json={
            "title": "Mercado",
            "type": "expense",
            "amount": 120000,
            "due_date": (today + timedelta(days=1)).isoformat(),
            "account_id": cash_id,
            "payment_method": "cash",
            "status": "pending",
        },
        headers=headers,
    )

    resp = await client.get("/api/v1/events/availability", params={"days": 7}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["cash_needed"] == 70000


@pytest.mark.anyio
async def test_availability_budget_committed(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "budget@example.com",
        "name": "Budget User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    cat = await client.post(
        "/api/v1/categories",
        json={"name": "Comida", "type": "expense"},
        headers=headers,
    )
    category_id = cat.json()["id"]

    await client.post(
        "/api/v1/budgets",
        json={
            "category_id": category_id,
            "amount": 500000,
            "month": date.today().month,
            "year": date.today().year,
        },
        headers=headers,
    )

    me = await client.get("/api/v1/auth/me", headers=headers)
    household_id = me.json()["household_id"]

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Banco", "type": "bank", "balance": 1000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    async with test_session_factory() as session:
        session.add(TransactionModel(
            id=str(uuid.uuid4()),
            account_id=account_id,
            user_id=me.json()["id"],
            type="expense",
            amount=Decimal("120000.00"),
            description="Almuerzo",
            date=date.today(),
            category_id=category_id,
        ))
        await session.commit()

    async with test_session_factory() as session:
        service = _make_service(session)
        result = await service.availability(household_id, 7)
        assert result["budget_committed"] == 120000

