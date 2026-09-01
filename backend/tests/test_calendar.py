import pytest
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import test_session_factory
from app.infrastructure.models.models import HouseholdModel, UserModel, FinancialEventModel
from app.application.services.event_service import FinancialEventService


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_create_obligation_generates_events(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "obl@example.com",
        "name": "Obl User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    response = await client.post(
        "/api/v1/obligations",
        json={
            "name": "Internet",
            "type": "expense",
            "amount": 85000,
            "anchor_day": 25,
            "recommended_offset_days": 5,
            "generate_months": 2,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    obligation = response.json()
    assert obligation["anchor_day"] == 25

    sept = await client.get(
        "/api/v1/events",
        params={"year": 2026, "month": 9},
        headers=headers,
    )
    octo = await client.get(
        "/api/v1/events",
        params={"year": 2026, "month": 10},
        headers=headers,
    )
    assert sept.status_code == 200 and octo.status_code == 200
    sept_events = [e for e in sept.json() if e["title"] == "Internet"]
    octo_events = [e for e in octo.json() if e["title"] == "Internet"]
    assert len(sept_events) == 1, sept_events
    assert len(octo_events) == 1, octo_events
    event = sept_events[0]
    assert event["due_date"] == "2026-09-25"
    assert event["recommended_date"] == "2026-09-20"
    assert event["visibility"] == "confirmed"
    assert event["obligation_id"] == obligation["id"]


@pytest.mark.anyio
async def test_create_manual_event_and_mark_paid(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "evt@example.com",
        "name": "Evt User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    created = await client.post(
        "/api/v1/events",
        json={
            "title": "Tarjeta",
            "type": "debt",
            "amount": 450000,
            "due_date": "2026-09-22",
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]

    paid = await client.post(f"/api/v1/events/{event_id}/pay", headers=headers)
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"

    fetched = await client.get(f"/api/v1/events/{event_id}", headers=headers)
    assert fetched.json()["status"] == "paid"


@pytest.mark.anyio
async def test_mark_paid_notifies_other_household_members():
    async with test_session_factory() as session:
        household_id = str(uuid.uuid4())
        session.add(HouseholdModel(id=household_id, name="Familia"))
        user1 = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        session.add(UserModel(
            id=user1, email="u1@x.com", name="Oscar", password_hash="x",
            role="owner", household_id=household_id,
        ))
        session.add(UserModel(
            id=user2, email="u2@x.com", name="Esposa", password_hash="x",
            role="member", household_id=household_id,
        ))
        event_id = str(uuid.uuid4())
        session.add(FinancialEventModel(
            id=event_id,
            household_id=household_id,
            source="USER",
            type="debt",
            title="Tarjeta",
            amount=Decimal("450000.00"),
            due_date=date(2026, 9, 22),
            status="pending",
        ))
        await session.commit()

        service = FinancialEventService(session)
        user = {"id": user1, "household_id": household_id, "name": "Oscar"}
        await service.mark_as_paid(event_id, user)
        await session.commit()

        from app.infrastructure.repositories.notification_repository import SQLAlchemyNotificationRepository
        noti_repo = SQLAlchemyNotificationRepository(session)
        member_notifs = await noti_repo.get_all(household_id, user_id=user2)
        assert len(member_notifs) == 1
        assert member_notifs[0]["title"] == "Tarjeta ya está pagado"


@pytest.mark.anyio
async def test_sync_debt_creates_obligation_and_events(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "debt@example.com",
        "name": "Debt User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    debt = await client.post(
        "/api/v1/debts",
        json={
            "name": "Tarjeta Crédito",
            "total_amount": 450000,
            "current_balance": 450000,
            "minimum_payment": 450000,
            "due_day": 25,
            "interest_rate": 0,
        },
        headers=headers,
    )
    assert debt.status_code == 201, debt.text
    debt_id = debt.json()["id"]

    obligations = await client.get("/api/v1/obligations", headers=headers)
    assert obligations.status_code == 200
    sys_obligations = [o for o in obligations.json() if o.get("source") == "SYSTEM" and o.get("source_id") == debt_id]
    assert len(sys_obligations) == 1
    assert sys_obligations[0]["type"] == "debt"
    assert sys_obligations[0]["anchor_day"] == 25

    events = await client.get(
        "/api/v1/events",
        params={"year": 2026, "month": 9},
        headers=headers,
    )
    assert events.status_code == 200
    debt_events = [e for e in events.json() if e["title"] == "Tarjeta Crédito"]
    assert len(debt_events) == 1
    assert debt_events[0]["due_date"] == "2026-09-25"


@pytest.mark.anyio
async def test_sync_recurring_creates_obligation_and_events(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "recur@example.com",
        "name": "Recur User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Bancolombia", "type": "bank", "balance": 1000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    recurring = await client.post(
        "/api/v1/recurring-payments",
        json={
            "account_id": account_id,
            "name": "Internet",
            "amount": 85000,
            "type": "expense",
            "frequency": "monthly",
            "day_of_month": 25,
            "next_due_date": "2026-09-25",
        },
        headers=headers,
    )
    assert recurring.status_code == 201, recurring.text
    recurring_id = recurring.json()["id"]

    obligations = await client.get("/api/v1/obligations", headers=headers)
    sys_obligations = [o for o in obligations.json() if o.get("source") == "SYSTEM" and o.get("source_id") == recurring_id]
    assert len(sys_obligations) == 1
    assert sys_obligations[0]["anchor_day"] == 25

    events = await client.get(
        "/api/v1/events",
        params={"year": 2026, "month": 9},
        headers=headers,
    )
    internet_events = [e for e in events.json() if e["title"] == "Internet"]
    assert len(internet_events) == 1
    assert internet_events[0]["due_date"] == "2026-09-25"


@pytest.mark.anyio
async def test_sync_debt_delete_removes_obligation(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "debtdel@example.com",
        "name": "DebtDel User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    debt = await client.post(
        "/api/v1/debts",
        json={
            "name": "Préstamo",
            "total_amount": 1000000,
            "current_balance": 1000000,
            "minimum_payment": 100000,
            "due_day": 10,
            "interest_rate": 0,
        },
        headers=headers,
    )
    debt_id = debt.json()["id"]

    obligations_before = await client.get("/api/v1/obligations", headers=headers)
    sys_obs = [o for o in obligations_before.json() if o.get("source_id") == debt_id]
    assert len(sys_obs) == 1

    await client.delete(f"/api/v1/debts/{debt_id}", headers=headers)
    assert True  # 204

    obligations_after = await client.get("/api/v1/obligations", headers=headers)
    sys_obs_after = [o for o in obligations_after.json() if o.get("source_id") == debt_id]
    assert len(sys_obs_after) == 0


@pytest.mark.anyio
async def test_create_obligation_from_event(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "fromevt@example.com",
        "name": "FromEvt User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    me = await client.get("/api/v1/auth/me", headers=headers)
    household_id = me.json()["household_id"]

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Bancolombia", "type": "bank", "balance": 1000000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    created = await client.post(
        "/api/v1/events",
        json={
            "title": "Internet",
            "type": "expense",
            "amount": 85000,
            "due_date": "2026-09-25",
            "recommended_date": "2026-09-20",
            "cutoff_date": "2026-09-23",
            "account_id": account_id,
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]

    from_event = await client.post(
        "/api/v1/obligations/from-event",
        json={"event_id": event_id},
        headers=headers,
    )
    assert from_event.status_code == 201, from_event.text
    obligation = from_event.json()
    assert obligation["name"] == "Internet"
    assert obligation["anchor_day"] == 25
    assert obligation["recommended_offset_days"] == 5
    assert obligation["cutoff_offset_days"] == 2

    events = await client.get(
        "/api/v1/events",
        params={"year": 2026, "month": 10},
        headers=headers,
    )
    assert events.status_code == 200
    oct_events = [e for e in events.json() if e["title"] == "Internet"]
    assert len(oct_events) == 1
    assert oct_events[0]["obligation_id"] == obligation["id"]

