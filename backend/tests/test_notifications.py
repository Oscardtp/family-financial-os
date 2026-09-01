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
)
from app.application.services.notification_service import NotificationService
from app.application.services.event_service import FinancialEventService


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_get_upcoming_groups_today_and_this_week(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "notif@example.com",
        "name": "Notif User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    today = date.today()
    tomorrow = today + timedelta(days=1)
    in_three = today + timedelta(days=3)
    in_seven = today + timedelta(days=7)

    await client.post(
        "/api/v1/events",
        json={
            "title": "Internet",
            "type": "expense",
            "amount": 85000,
            "due_date": today.isoformat(),
            "status": "pending",
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/events",
        json={
            "title": "Tarjeta",
            "type": "debt",
            "amount": 450000,
            "due_date": tomorrow.isoformat(),
            "status": "pending",
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/events",
        json={
            "title": "Netflix",
            "type": "expense",
            "amount": 38000,
            "due_date": in_three.isoformat(),
            "status": "pending",
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/events",
        json={
            "title": "Spotify",
            "type": "expense",
            "amount": 16000,
            "due_date": in_seven.isoformat(),
            "status": "pending",
        },
        headers=headers,
    )

    resp = await client.get("/api/v1/notifications/upcoming", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert "today" in body
    assert "this_week" in body
    assert len(body["today"]) == 1
    assert body["today"][0]["title"] == "Internet"
    assert body["today"][0]["level"] == "Hoy"
    assert len(body["this_week"]) == 3


@pytest.mark.anyio
async def test_get_upcoming_does_not_include_paid_events(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "notif2@example.com",
        "name": "Notif2 User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    today = date.today()
    created = await client.post(
        "/api/v1/events",
        json={
            "title": "Arriendo",
            "type": "expense",
            "amount": 500000,
            "due_date": today.isoformat(),
            "status": "pending",
        },
        headers=headers,
    )
    event_id = created.json()["id"]
    await client.post(f"/api/v1/events/{event_id}/pay", headers=headers)

    resp = await client.get("/api/v1/notifications/upcoming", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["today"] == []
    assert body["this_week"] == []


@pytest.mark.anyio
async def test_get_upcoming_includes_overdue_as_pending(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "notif3@example.com",
        "name": "Notif3 User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    yesterday = date.today() - timedelta(days=1)
    await client.post(
        "/api/v1/events",
        json={
            "title": "Servicio luz",
            "type": "expense",
            "amount": 120000,
            "due_date": yesterday.isoformat(),
            "status": "pending",
        },
        headers=headers,
    )

    resp = await client.get("/api/v1/notifications/upcoming", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["today"]) == 1
    assert body["today"][0]["title"] == "Servicio luz"
    assert body["today"][0]["level"] == "Pendiente"


@pytest.mark.anyio
async def test_get_upcoming_only_current_user_household(client):
    reg1 = await client.post("/api/v1/auth/register", json={
        "email": "notifA@example.com",
        "name": "Notif A",
        "password": "password123",
    })
    token_a = reg1.json()["access_token"]
    headers_a = _auth_headers(token_a)

    reg2 = await client.post("/api/v1/auth/register", json={
        "email": "notifB@example.com",
        "name": "Notif B",
        "password": "password123",
    })
    token_b = reg2.json()["access_token"]
    headers_b = _auth_headers(token_b)

    today = date.today()
    await client.post(
        "/api/v1/events",
        json={
            "title": "Evento A",
            "type": "expense",
            "amount": 50000,
            "due_date": today.isoformat(),
            "status": "pending",
        },
        headers=headers_a,
    )
    await client.post(
        "/api/v1/events",
        json={
            "title": "Evento B",
            "type": "expense",
            "amount": 70000,
            "due_date": today.isoformat(),
            "status": "pending",
        },
        headers=headers_b,
    )

    resp_a = await client.get("/api/v1/notifications/upcoming", headers=headers_a)
    body_a = resp_a.json()
    titles_a = [item["title"] for group in body_a.values() for item in group]
    assert "Evento A" in titles_a
    assert "Evento B" not in titles_a
