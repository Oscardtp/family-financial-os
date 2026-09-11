"""Tests for account deletion with recurring payments."""
import pytest
from uuid import uuid4
from datetime import date
from decimal import Decimal


@pytest.mark.anyio
async def test_delete_account_with_recurring_payments_succeeds(client):
    """Deleting an account that has recurring payments should succeed
    and leave the recurring payments with account_id=None."""
    # Register user
    reg = await client.post("/api/v1/auth/register", json={
        "email": "delete-test@example.com",
        "name": "Delete Test",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create account
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Test Account", "type": "bank", "balance": 100000},
        headers=headers,
    )
    assert acc_resp.status_code == 201
    account_id = acc_resp.json()["id"]

    # Create recurring payment tied to that account
    pay_resp = await client.post(
        "/api/v1/recurring-payments",
        json={
            "name": "Test Subscription",
            "amount": 50000,
            "type": "expense",
            "frequency": "monthly",
            "day_of_month": 1,
            "account_id": account_id,
        },
        headers=headers,
    )
    assert pay_resp.status_code == 201
    payment_id = pay_resp.json()["id"]

    # Delete the account
    del_resp = await client.delete(f"/api/v1/accounts/{account_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verify recurring payment still exists but account_id is null
    get_resp = await client.get(f"/api/v1/recurring-payments/{payment_id}", headers=headers)
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["account_id"] is None


@pytest.mark.anyio
async def test_delete_account_without_recurring_payments_succeeds(client):
    """Deleting an account with no recurring payments should work normally."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": "simple-delete@example.com",
        "name": "Simple Delete",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Orphan Account", "type": "cash", "balance": 50000},
        headers=headers,
    )
    assert acc_resp.status_code == 201
    account_id = acc_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/accounts/{account_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verify account is gone
    get_resp = await client.get(f"/api/v1/accounts/{account_id}", headers=headers)
    assert get_resp.status_code == 404