import pytest
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.config import get_settings

settings = get_settings()


def _make_token(sub=None, exp_delta=None, token_type="access"):
    sub = sub or str(uuid.uuid4())
    payload = {"sub": sub, "type": token_type}
    if exp_delta is not None:
        payload["exp"] = datetime.now(timezone.utc) + exp_delta
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest.mark.anyio
async def test_expired_token_rejected(client):
    token = _make_token(exp_delta=timedelta(seconds=-1))
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_refresh_token_not_accepted_as_access(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "refresh_test@example.com", "name": "Refresh", "password": "password123",
    })
    refresh_token = reg.json()["refresh_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_malformed_token_rejected(client):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt-token"})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_invalid_sub_rejected(client):
    token = _make_token(sub="not-a-uuid")
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_password_hash_not_exposed(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "hash_hide@example.com", "name": "Hash", "password": "password123",
    })
    token = reg.json()["access_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "password_hash" not in data
    assert "password" not in data


@pytest.mark.anyio
async def test_viewer_cannot_create_transaction(client):
    owner = await client.post("/api/v1/auth/register", json={
        "email": "viewer_tx_owner@example.com", "name": "Owner", "password": "password123",
    })
    owner_headers = {"Authorization": f"Bearer {owner.json()['access_token']}"}

    acc = await client.post("/api/v1/accounts",
        json={"name": "Cta", "type": "bank", "balance": 100000}, headers=owner_headers)
    account_id = acc.json()["id"]

    viewer = await client.post("/api/v1/auth/register", json={
        "email": "viewer_tx@example.com", "name": "Viewer", "password": "password123",
    })
    viewer_headers = {"Authorization": f"Bearer {viewer.json()['access_token']}"}

    resp = await client.post("/api/v1/transactions", json={
        "account_id": account_id, "type": "income", "amount": 1000,
        "description": "Should fail", "date": "2026-08-27",
    }, headers=viewer_headers)
    assert resp.status_code in (400, 401, 403, 404)


@pytest.mark.anyio
async def test_viewer_cannot_delete_account(client):
    owner = await client.post("/api/v1/auth/register", json={
        "email": "viewer_del_owner@example.com", "name": "Owner", "password": "password123",
    })
    owner_headers = {"Authorization": f"Bearer {owner.json()['access_token']}"}

    acc = await client.post("/api/v1/accounts",
        json={"name": "Cta", "type": "bank", "balance": 100000}, headers=owner_headers)
    account_id = acc.json()["id"]

    viewer = await client.post("/api/v1/auth/register", json={
        "email": "viewer_del@example.com", "name": "Viewer", "password": "password123",
    })
    viewer_headers = {"Authorization": f"Bearer {viewer.json()['access_token']}"}

    resp = await client.delete(f"/api/v1/accounts/{account_id}", headers=viewer_headers)
    assert resp.status_code in (400, 401, 403, 404)


@pytest.mark.anyio
async def test_login_wrong_password_rejected(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong_pw@example.com", "name": "Wrong", "password": "password123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrong_pw@example.com", "password": "wrong_password",
    })
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_duplicate_email_rejected(client):
    await client.post("/api/v1/auth/register", json={
        "email": "dup@example.com", "name": "Dup", "password": "password123",
    })
    resp = await client.post("/api/v1/auth/register", json={
        "email": "dup@example.com", "name": "Dup2", "password": "password123",
    })
    assert resp.status_code == 400
