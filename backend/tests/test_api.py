import pytest


@pytest.mark.anyio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_register_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.anyio
async def test_login_user(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "name": "Login User",
        "password": "password123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_get_me(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "name": "Me User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.anyio
async def test_create_account(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "account@example.com",
        "name": "Account User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    response = await client.post(
        "/api/v1/accounts",
        json={"name": "Savings", "type": "bank", "balance": 1000},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Savings"
    assert data["balance"] == "1000.00"


@pytest.mark.anyio
async def test_create_transaction(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "tx@example.com",
        "name": "TX User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 5000},
        headers=headers,
    )
    account_id = acc.json()["id"]

    response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "type": "income",
            "amount": 1000,
            "description": "Salary",
            "date": "2026-01-15",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "1000.00"
    assert data["type"] == "income"
