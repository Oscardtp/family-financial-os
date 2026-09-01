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
    DebtModel,
    RecurringPaymentModel,
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
async def test_prepare_month_summary(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "prepare@example.com",
        "name": "Prepare User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Bancolombia", "type": "bank", "balance": 3000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    today = date.today()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1)
    else:
        month_end = date(today.year, today.month + 1, 1)

    for i in range(3):
        d = month_start + timedelta(days=i + 1)
        await client.post(
            "/api/v1/events",
            json={
                "title": f"Pago {i}",
                "type": "expense",
                "amount": 120000,
                "due_date": d.isoformat(),
                "account_id": account_id,
                "status": "pending",
            },
            headers=headers,
        )

    await client.post(
        "/api/v1/events",
        json={
            "title": "Salario",
            "type": "income",
            "amount": 2500000,
            "due_date": (month_start + timedelta(days=5)).isoformat(),
            "status": "pending",
        },
        headers=headers,
    )

    resp = await client.get("/api/v1/month/prepare", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["scheduled_payments_count"] == 3
    assert body["scheduled_payments_amount"] == 360000
    assert body["expected_income"] == 2500000
    assert "month" in body


@pytest.mark.anyio
async def test_prepare_month_includes_new_debts(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "prepare2@example.com",
        "name": "Prepare2 User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    await client.post(
        "/api/v1/debts",
        json={
            "name": "Préstamo nuevo",
            "total_amount": 1000000,
            "current_balance": 1000000,
            "minimum_payment": 100000,
            "due_day": today.day if False else 15,
            "interest_rate": 0,
        },
        headers=headers,
    )

    resp = await client.get("/api/v1/month/prepare", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["new_debts_count"] >= 1
