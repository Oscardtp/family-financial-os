"""Tests for Recurring Payment History endpoint.

FASE 5.1 — Backend History API
"""
import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.infrastructure.models.models import Base, HouseholdModel, UserModel, AccountModel, RecurringPaymentModel, TransactionModel


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
    recurring_id = "rp1"

    household = HouseholdModel(id=household_id, name="Test Household")
    db_session.add(household)

    user = UserModel(id=user_id, email="test@test.com", name="Test User", password_hash="x", household_id=household_id)
    db_session.add(user)

    account = AccountModel(id=account_id, household_id=household_id, name="Cuenta Principal", type="checking", balance=Decimal("1000000"))
    db_session.add(account)

    recurring = RecurringPaymentModel(
        id=recurring_id, household_id=household_id, account_id=account_id,
        name="Netflix", amount=Decimal("45000"), type="expense",
        frequency="monthly", day_of_month=15, next_due_date=date(2026, 10, 15),
    )
    db_session.add(recurring)

    tx1 = TransactionModel(
        id="tx1", household_id=household_id, account_id=account_id,
        user_id=user_id, type="expense", amount=Decimal("45000"),
        description="Netflix", date=date(2026, 8, 15), recurring_payment_id=recurring_id,
    )
    tx2 = TransactionModel(
        id="tx2", household_id=household_id, account_id=account_id,
        user_id=user_id, type="expense", amount=Decimal("45000"),
        description="Netflix", date=date(2026, 9, 15), recurring_payment_id=recurring_id,
    )
    tx_other = TransactionModel(
        id="tx-other", household_id=household_id, account_id=account_id,
        user_id=user_id, type="expense", amount=Decimal("50000"),
        description="Spotify", date=date(2026, 9, 10), recurring_payment_id=None,
    )
    db_session.add_all([tx1, tx2, tx_other])
    await db_session.commit()
    return {"household_id": household_id, "recurring_id": recurring_id, "user_id": user_id}


@pytest.mark.asyncio
async def test_history_returns_transactions(db_session, seed_data):
    """GET /recurring-payments/{id}/payments must return linked transactions."""
    from app.application.services.recurring_payment_history_service import RecurringPaymentHistoryService
    service = RecurringPaymentHistoryService(db_session)
    result = await service.get_payments(seed_data["recurring_id"], seed_data["household_id"])
    assert len(result) == 2


@pytest.mark.asyncio
async def test_history_ordered_by_date(db_session, seed_data):
    """History must be ordered by date descending (most recent first)."""
    from app.application.services.recurring_payment_history_service import RecurringPaymentHistoryService
    service = RecurringPaymentHistoryService(db_session)
    result = await service.get_payments(seed_data["recurring_id"], seed_data["household_id"])
    dates = [r["date"] for r in result]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.asyncio
async def test_empty_history_returns_empty_list(db_session, seed_data):
    """Non-existent recurring payment must return empty list, not 404."""
    from app.application.services.recurring_payment_history_service import RecurringPaymentHistoryService
    service = RecurringPaymentHistoryService(db_session)
    result = await service.get_payments("nonexistent", seed_data["household_id"])
    assert result == []


@pytest.mark.asyncio
async def test_history_is_household_scoped(db_session, seed_data):
    """History must only return transactions from the same household."""
    from app.application.services.recurring_payment_history_service import RecurringPaymentHistoryService
    service = RecurringPaymentHistoryService(db_session)
    result = await service.get_payments(seed_data["recurring_id"], "other-household")
    assert result == []


@pytest.mark.asyncio
async def test_unrelated_transactions_excluded(db_session, seed_data):
    """Transactions without recurring_payment_id must be excluded."""
    from app.application.services.recurring_payment_history_service import RecurringPaymentHistoryService
    service = RecurringPaymentHistoryService(db_session)
    result = await service.get_payments(seed_data["recurring_id"], seed_data["household_id"])
    tx_ids = [r["id"] for r in result]
    assert "tx-other" not in tx_ids
