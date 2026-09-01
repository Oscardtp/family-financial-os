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
    TransactionModel,
    CategoryModel,
)
from app.application.services.learning_service import LearningService


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_detect_patterns_returns_suggestions(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "learn@example.com",
        "name": "Learn User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    me = await client.get("/api/v1/auth/me", headers=headers)
    household_id = me.json()["household_id"]

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Banco", "type": "bank", "balance": 1000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    base = date.today() - timedelta(days=21)
    for i in range(3):
        await client.post(
            "/api/v1/transactions",
            json={
                "account_id": account_id,
                "type": "expense",
                "amount": 85000,
                "description": "Internet",
                "date": (base + timedelta(days=i * 2)).isoformat(),
            },
            headers=headers,
        )

    async with test_session_factory() as session:
        from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
        tx_repo = SQLAlchemyTransactionRepository(session)
        txs = await tx_repo.get_all(household_id, limit=500)
        print('DEBUG TXS:', txs)
        service = LearningService(session)
        suggestions = await service.detect_patterns(household_id)
        print('DEBUG SUGGESTIONS:', suggestions)
        assert len(suggestions) == 1
        assert suggestions[0]["name"] == "Internet"
        assert suggestions[0]["confidence"] >= 60
        assert suggestions[0]["type"] == "expense"


@pytest.mark.anyio
async def test_detect_patterns_ignores_noise(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "learn2@example.com",
        "name": "Learn2 User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    me = await client.get("/api/v1/auth/me", headers=headers)
    household_id = me.json()["household_id"]

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Banco", "type": "bank", "balance": 1000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    base = date.today() - timedelta(days=20)
    for i in range(2):
        await client.post(
            "/api/v1/transactions",
            json={
                "account_id": account_id,
                "type": "expense",
                "amount": 50000 + i * 10000,
                "description": "Aleatorio",
                "date": (base + timedelta(days=i * 10)).isoformat(),
            },
            headers=headers,
        )

    async with test_session_factory() as session:
        service = LearningService(session)
        suggestions = await service.detect_patterns(household_id)
        assert suggestions == []


@pytest.mark.anyio
async def test_detect_patterns_does_not_create_obligations(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "learn3@example.com",
        "name": "Learn3 User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    me = await client.get("/api/v1/auth/me", headers=headers)
    household_id = me.json()["household_id"]

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Banco", "type": "bank", "balance": 1000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    base = date.today() - timedelta(days=28)
    for i in range(3):
        await client.post(
            "/api/v1/transactions",
            json={
                "account_id": account_id,
                "type": "expense",
                "amount": 90000,
                "description": "Netflix",
                "date": (base + timedelta(days=i * 7)).isoformat(),
            },
            headers=headers,
        )

    async with test_session_factory() as session:
        service = LearningService(session)
        suggestions = await service.detect_patterns(household_id)
        assert suggestions == []
        obligations = await client.get("/api/v1/obligations", headers=headers)
        assert not any(o.get("source") == "LEARNED" for o in obligations.json())


@pytest.mark.anyio
async def test_coach_patterns_endpoint_returns_suggestions(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "pattern@example.com",
        "name": "Pattern User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    me = await client.get("/api/v1/auth/me", headers=headers)
    household_id = me.json()["household_id"]

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Banco", "type": "bank", "balance": 1000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    base = date.today() - timedelta(days=21)
    for i in range(3):
        await client.post(
            "/api/v1/transactions",
            json={
                "account_id": account_id,
                "type": "expense",
                "amount": 90000,
                "description": "Mercado",
                "date": (base + timedelta(days=i * 2)).isoformat(),
            },
            headers=headers,
        )

    patterns = await client.get("/api/v1/coach/patterns", headers=headers)
    assert patterns.status_code == 200
    data = patterns.json()
    assert len(data) == 1
    assert data[0]["name"] == "Mercado"
    assert data[0]["confidence"] >= 60
