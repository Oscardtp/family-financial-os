"""Tests for account update with balance."""
import pytest


@pytest.mark.anyio
async def test_update_account_balance(client):
    """Updating an account's balance should persist the new value."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": "balance-update@example.com",
        "name": "Balance Update",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create account
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Test", "type": "bank", "balance": 100000},
        headers=headers,
    )
    assert acc_resp.status_code == 201
    account_id = acc_resp.json()["id"]

    # Update balance
    update_resp = await client.put(
        f"/api/v1/accounts/{account_id}",
        json={"balance": 250000},
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["balance"] == "250000.00"
    assert data["name"] == "Test"  # unchanged