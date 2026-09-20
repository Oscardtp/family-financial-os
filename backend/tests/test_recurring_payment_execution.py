"""Tests for Recurring Payment Execution via Financial Events (FASE 5.3).

The correct flow:
  RecurringPayment → FinancialEvent (pending) → POST /events/{id}/pay → Transaction

Tests cover:
1. mark_as_paid creates Transaction for recurring payment events
2. Transaction links back to RecurringPayment via recurring_payment_id
3. Account balance is updated
4. RecurringPayment next_due_date advances
5. Idempotency (already-paid event returns existing)
6. Pending event endpoint returns correct event
"""
import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.infrastructure.models.models import (
    Base, HouseholdModel, UserModel, AccountModel,
    RecurringPaymentModel, TransactionModel, CategoryModel,
    FinancialObligationModel, FinancialEventModel,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def seed_data(db_session):
    household_id = "h1"
    user_id = "u1"
    account_id = "a1"
    category_id = "cat1"
    recurring_id = "rp1"
    obligation_id = "ob1"
    event_id = "ev1"

    db_session.add_all([
        HouseholdModel(id=household_id, name="Test Household"),
        UserModel(
            id=user_id, email="test@test.com", name="Test User",
            password_hash="x", household_id=household_id,
        ),
        AccountModel(
            id=account_id, household_id=household_id, name="Cuenta Principal",
            type="checking", balance=Decimal("1000000"),
        ),
        CategoryModel(
            id=category_id, household_id=household_id, name="Servicios",
            type="expense",
        ),
        RecurringPaymentModel(
            id=recurring_id, household_id=household_id, account_id=account_id,
            category_id=category_id, name="Netflix", amount=Decimal("45000"),
            type="expense", frequency="monthly", day_of_month=15,
            next_due_date=date(2026, 10, 15), is_active=True,
        ),
        FinancialObligationModel(
            id=obligation_id, household_id=household_id,
            source="SYSTEM", source_id=recurring_id,
            name="Netflix", type="expense",
            amount=Decimal("45000"), currency="COP",
            frequency="monthly", anchor_day=15,
            is_active=True, confidence=100,
        ),
        FinancialEventModel(
            id=event_id, household_id=household_id,
            source="SYSTEM", source_id=obligation_id,
            type="expense", title="Netflix",
            amount=Decimal("45000"), currency="COP",
            due_date=date(2026, 9, 15),
            status="pending", is_recurrent=True,
            recurrence_group_id=obligation_id,
            obligation_id=obligation_id,
            account_id=account_id, category_id=category_id,
            confirmed=True, visibility="confirmed",
            confidence=100, reminder_days_before=3,
        ),
    ])
    await db_session.commit()

    return {
        "household_id": household_id,
        "user_id": user_id,
        "account_id": account_id,
        "category_id": category_id,
        "recurring_id": recurring_id,
        "obligation_id": obligation_id,
        "event_id": event_id,
    }


# --- Service-level tests ---

@pytest.mark.asyncio
async def test_mark_as_paid_creates_transaction(db_session, seed_data):
    """mark_as_paid on a recurring event must create a Transaction."""
    from app.application.services.event_service import FinancialEventService

    user = {"id": seed_data["user_id"], "household_id": seed_data["household_id"]}
    service = FinancialEventService(db_session)
    result = await service.mark_as_paid(seed_data["event_id"], user)

    assert result["status"] == "paid"

    tx_repo = __import__(
        "app.infrastructure.repositories.transaction_repository",
        fromlist=["SQLAlchemyTransactionRepository"],
    ).SQLAlchemyTransactionRepository(db_session)
    txs = await tx_repo.get_by_recurring(
        seed_data["recurring_id"], seed_data["household_id"]
    )
    assert len(txs) == 1
    assert txs[0]["recurring_payment_id"] == seed_data["recurring_id"]


@pytest.mark.asyncio
async def test_transaction_amount_is_decimal(db_session, seed_data):
    """Transaction amount must be Decimal with 2 places."""
    from app.application.services.event_service import FinancialEventService

    user = {"id": seed_data["user_id"], "household_id": seed_data["household_id"]}
    service = FinancialEventService(db_session)
    await service.mark_as_paid(seed_data["event_id"], user)

    tx_repo = __import__(
        "app.infrastructure.repositories.transaction_repository",
        fromlist=["SQLAlchemyTransactionRepository"],
    ).SQLAlchemyTransactionRepository(db_session)
    txs = await tx_repo.get_by_recurring(
        seed_data["recurring_id"], seed_data["household_id"]
    )
    amount = txs[0]["amount"]
    assert isinstance(amount, Decimal)
    assert amount == Decimal("45000.00")


@pytest.mark.asyncio
async def test_account_balance_deducted(db_session, seed_data):
    """Expense event must deduct from account balance."""
    from app.application.services.event_service import FinancialEventService

    acc_repo = __import__(
        "app.infrastructure.repositories.account_repository",
        fromlist=["SQLAlchemyAccountRepository"],
    ).SQLAlchemyAccountRepository(db_session)
    before = await acc_repo.get_by_id(seed_data["account_id"])

    user = {"id": seed_data["user_id"], "household_id": seed_data["household_id"]}
    service = FinancialEventService(db_session)
    await service.mark_as_paid(seed_data["event_id"], user)

    after = await acc_repo.get_by_id(seed_data["account_id"])
    assert after["balance"] == before["balance"] - Decimal("45000.00")


@pytest.mark.asyncio
async def test_recurring_payment_next_due_advances(db_session, seed_data):
    """After payment, RecurringPayment next_due_date must advance from today."""
    from app.application.services.event_service import FinancialEventService
    from app.infrastructure.models.models import RecurringPaymentModel

    rp = await db_session.get(RecurringPaymentModel, seed_data["recurring_id"])
    rp.next_due_date = date(2026, 9, 1)
    await db_session.commit()

    rp_repo = __import__(
        "app.infrastructure.repositories.recurring_payment_repository",
        fromlist=["SQLAlchemyRecurringPaymentRepository"],
    ).SQLAlchemyRecurringPaymentRepository(db_session)
    before = await rp_repo.get_by_id(seed_data["recurring_id"])

    user = {"id": seed_data["user_id"], "household_id": seed_data["household_id"]}
    service = FinancialEventService(db_session)
    await service.mark_as_paid(seed_data["event_id"], user)

    after = await rp_repo.get_by_id(seed_data["recurring_id"])
    assert after["next_due_date"] > before["next_due_date"]


@pytest.mark.asyncio
async def test_idempotency_already_paid(db_session, seed_data):
    """Calling mark_as_paid twice must not create duplicate transactions."""
    from app.application.services.event_service import FinancialEventService

    user = {"id": seed_data["user_id"], "household_id": seed_data["household_id"]}
    service = FinancialEventService(db_session)
    await service.mark_as_paid(seed_data["event_id"], user)
    await service.mark_as_paid(seed_data["event_id"], user)

    tx_repo = __import__(
        "app.infrastructure.repositories.transaction_repository",
        fromlist=["SQLAlchemyTransactionRepository"],
    ).SQLAlchemyTransactionRepository(db_session)
    txs = await tx_repo.get_by_recurring(
        seed_data["recurring_id"], seed_data["household_id"]
    )
    assert len(txs) == 1


@pytest.mark.asyncio
async def test_transaction_has_correct_fields(db_session, seed_data):
    """Transaction must have account_id, category_id, type, description, recurring_payment_id."""
    from app.application.services.event_service import FinancialEventService

    user = {"id": seed_data["user_id"], "household_id": seed_data["household_id"]}
    service = FinancialEventService(db_session)
    await service.mark_as_paid(seed_data["event_id"], user)

    tx_repo = __import__(
        "app.infrastructure.repositories.transaction_repository",
        fromlist=["SQLAlchemyTransactionRepository"],
    ).SQLAlchemyTransactionRepository(db_session)
    txs = await tx_repo.get_by_recurring(
        seed_data["recurring_id"], seed_data["household_id"]
    )
    tx = txs[0]
    assert tx["account_id"] == seed_data["account_id"]
    assert tx["category_id"] == seed_data["category_id"]
    assert tx["type"] == "expense"
    assert "Netflix" in tx["description"]
    assert tx["recurring_payment_id"] == seed_data["recurring_id"]


# --- Endpoint-level tests ---

def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_pending_event_endpoint(client: AsyncClient):
    """GET /recurring-payments/{id}/pending-event returns the pending FinancialEvent."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": "pe1@test.com", "name": "PE Test", "password": "test123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    acc = await client.post("/api/v1/accounts", headers=headers, json={
        "name": "Cuenta", "type": "bank", "balance": "1000000",
    })
    account_id = acc.json()["id"]

    rp = await client.post("/api/v1/recurring-payments", headers=headers, json={
        "name": "Spotify", "amount": "15000", "type": "expense",
        "frequency": "monthly", "day_of_month": 1,
    })
    rp_id = rp.json()["id"]

    resp = await client.get(
        f"/api/v1/recurring-payments/{rp_id}/pending-event",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "pending"
    assert body["is_recurrent"] is True


@pytest.mark.anyio
async def test_pending_event_not_found_for_nonexistent(client: AsyncClient):
    """GET /recurring-payments/{id}/pending-event returns 404 for non-existent payment."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": "pe2@test.com", "name": "PE Test 2", "password": "test123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    resp = await client.get(
        "/api/v1/recurring-payments/nonexistent/pending-event",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_execute_via_event_pay_creates_transaction(client: AsyncClient):
    """Full flow: GET pending-event → POST /events/{id}/pay → Transaction created."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": "pe3@test.com", "name": "PE Test 3", "password": "test123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    acc = await client.post("/api/v1/accounts", headers=headers, json={
        "name": "Cuenta", "type": "bank", "balance": "1000000",
    })

    rp = await client.post("/api/v1/recurring-payments", headers=headers, json={
        "name": "Internet", "amount": "120000", "type": "expense",
        "frequency": "monthly", "day_of_month": 5,
    })
    rp_id = rp.json()["id"]

    # Get pending event
    pe_resp = await client.get(
        f"/api/v1/recurring-payments/{rp_id}/pending-event",
        headers=headers,
    )
    assert pe_resp.status_code == 200
    event_id = pe_resp.json()["id"]

    # Mark as paid
    pay_resp = await client.post(
        f"/api/v1/events/{event_id}/pay",
        headers=headers,
    )
    assert pay_resp.status_code == 200
    assert pay_resp.json()["status"] == "paid"

    # Verify transaction was created
    history_resp = await client.get(
        f"/api/v1/recurring-payments/{rp_id}/payments",
        headers=headers,
    )
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) >= 1
    assert history[0]["recurring_payment_id"] == rp_id


@pytest.mark.anyio
async def test_execute_amount_is_numeric(client: AsyncClient):
    """Amount in history must be a numeric value with correct precision."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": "pe4@test.com", "name": "PE Test 4", "password": "test123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    acc = await client.post("/api/v1/accounts", headers=headers, json={
        "name": "Cuenta", "type": "bank", "balance": "1000000",
    })

    rp = await client.post("/api/v1/recurring-payments", headers=headers, json={
        "name": "Cable", "amount": "85000", "type": "expense",
        "frequency": "monthly", "day_of_month": 10,
    })
    rp_id = rp.json()["id"]

    pe_resp = await client.get(
        f"/api/v1/recurring-payments/{rp_id}/pending-event",
        headers=headers,
    )
    event_id = pe_resp.json()["id"]

    await client.post(f"/api/v1/events/{event_id}/pay", headers=headers)

    history_resp = await client.get(
        f"/api/v1/recurring-payments/{rp_id}/payments",
        headers=headers,
    )
    tx = history_resp.json()[0]
    assert float(tx["amount"]) == 85000.0
