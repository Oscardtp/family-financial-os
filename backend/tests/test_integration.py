import pytest
import uuid
from datetime import date


def unique_email(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
async def auth(client):
    email = unique_email("owner")
    reg = await client.post("/api/v1/auth/register", json={
        "email": email, "name": "Owner User", "password": "password123",
    })
    token = reg.json()["access_token"]
    return {"token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
async def member_auth(client, auth):
    email = unique_email("member")
    reg = await client.post("/api/v1/auth/register", json={
        "email": email, "name": "Member User", "password": "password123",
    })
    member_token = reg.json()["access_token"]
    member_headers = {"Authorization": f"Bearer {member_token}"}
    me = await client.get("/api/v1/auth/me", headers=member_headers)
    member_id = me.json()["id"]
    household = await client.get("/api/v1/household", headers=auth["headers"])
    await client.post(
        "/api/v1/household/invite",
        json={"email": email, "role": "member"},
        headers=auth["headers"],
    )
    return {"token": member_token, "headers": member_headers, "member_id": member_id}


# --- Role-based access tests ---

@pytest.mark.anyio
async def test_viewer_cannot_create_account(client, auth):
    email = unique_email("viewer")
    reg = await client.post("/api/v1/auth/register", json={
        "email": email, "name": "Viewer", "password": "password123",
    })
    viewer_headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    await client.post(
        "/api/v1/household/invite",
        json={"email": email, "role": "viewer"},
        headers=auth["headers"],
    )
    response = await client.post(
        "/api/v1/accounts",
        json={"name": "Test", "type": "bank", "balance": 0},
        headers=viewer_headers,
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_member_can_create_account(client, member_auth):
    response = await client.post(
        "/api/v1/accounts",
        json={"name": "Member Account", "type": "bank", "balance": 500},
        headers=member_auth["headers"],
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_member_cannot_delete_account(client, member_auth):
    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "To Delete", "type": "bank", "balance": 0},
        headers=member_auth["headers"],
    )
    account_id = acc.json()["id"]
    response = await client.delete(f"/api/v1/accounts/{account_id}", headers=member_auth["headers"])
    assert response.status_code == 403


@pytest.mark.anyio
async def test_owner_can_delete_account(client, auth):
    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Owner Del", "type": "bank", "balance": 0},
        headers=auth["headers"],
    )
    response = await client.delete(f"/api/v1/accounts/{acc.json()['id']}", headers=auth["headers"])
    assert response.status_code == 204


@pytest.mark.anyio
async def test_member_cannot_manage_household(client, member_auth):
    response = await client.post(
        "/api/v1/household/invite",
        json={"email": "new@example.com", "role": "member"},
        headers=member_auth["headers"],
    )
    assert response.status_code == 403


# --- Category tests ---

@pytest.mark.anyio
async def test_default_categories_on_register(client):
    email = unique_email("cats")
    reg = await client.post("/api/v1/auth/register", json={
        "email": email, "name": "Cat User", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    response = await client.get("/api/v1/categories", headers=headers)
    assert response.status_code == 200
    cats = response.json()
    assert len(cats) >= 10
    names = [c["name"] for c in cats]
    assert "Comida" in names
    assert "Salario" in names


@pytest.mark.anyio
async def test_create_category(client, auth):
    response = await client.post(
        "/api/v1/categories",
        json={"name": "Mascotas", "type": "expense", "icon": "paw-print", "color": "#a3a3a3"},
        headers=auth["headers"],
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Mascotas"


# --- Dashboard tests ---

@pytest.mark.anyio
async def test_dashboard_empty(client, auth):
    response = await client.get("/api/v1/dashboard", headers=auth["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["total_balance"] == "0"
    assert data["monthly_income"] == "0"
    assert data["monthly_expenses"] == "0"


@pytest.mark.anyio
async def test_dashboard_with_transactions(client, auth):
    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Main", "type": "bank", "balance": 0},
        headers=auth["headers"],
    )
    account_id = acc.json()["id"]
    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    mid_of_month = date(today.year, today.month, 5)
    await client.post(
        "/api/v1/transactions",
        json={"account_id": account_id, "type": "income", "amount": 5000, "description": "Salary", "date": first_of_month.isoformat()},
        headers=auth["headers"],
    )
    await client.post(
        "/api/v1/transactions",
        json={"account_id": account_id, "type": "expense", "amount": 1200, "description": "Rent", "date": mid_of_month.isoformat()},
        headers=auth["headers"],
    )
    response = await client.get("/api/v1/dashboard", headers=auth["headers"])
    data = response.json()
    assert data["monthly_income"] == "5000.00"
    assert data["monthly_expenses"] == "1200.00"
    assert data["net_monthly"] == "3800.00"


# --- CSV Export tests ---

@pytest.mark.anyio
async def test_export_csv(client, auth):
    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Exp", "type": "bank", "balance": 0},
        headers=auth["headers"],
    )
    account_id = acc.json()["id"]
    await client.post(
        "/api/v1/transactions",
        json={"account_id": account_id, "type": "income", "amount": 100, "description": "Test", "date": "2026-08-10"},
        headers=auth["headers"],
    )
    response = await client.get("/api/v1/reports/transactions/csv", headers=auth["headers"])
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    content = response.text
    assert "Fecha" in content
    assert "100" in content


@pytest.mark.anyio
async def test_export_csv_with_dates(client, auth):
    acc = await client.post(
        "/api/v1/accounts",
        json={"name": "Exp2", "type": "bank", "balance": 100},
        headers=auth["headers"],
    )
    account_id = acc.json()["id"]
    await client.post(
        "/api/v1/transactions",
        json={"account_id": account_id, "type": "expense", "amount": 50, "description": "Lunch", "date": "2026-08-12"},
        headers=auth["headers"],
    )
    response = await client.get(
        "/api/v1/reports/transactions/csv?start_date=2026-08-01&end_date=2026-08-15",
        headers=auth["headers"],
    )
    assert response.status_code == 200
    assert "50" in response.text


# --- Household tests ---

@pytest.mark.anyio
async def test_household_after_register(client, auth):
    response = await client.get("/api/v1/household", headers=auth["headers"])
    assert response.status_code == 200
    data = response.json()
    assert "members" in data
    assert len(data["members"]) == 1
    assert data["members"][0]["role"] == "owner"


@pytest.mark.anyio
async def test_invite_and_remove_member(client, auth):
    email = unique_email("remove")
    await client.post("/api/v1/auth/register", json={
        "email": email, "name": "Remove Me", "password": "password123",
    })
    invite = await client.post(
        "/api/v1/household/invite",
        json={"email": email, "role": "member"},
        headers=auth["headers"],
    )
    assert invite.status_code == 201
    household = await client.get("/api/v1/household", headers=auth["headers"])
    members = household.json()["members"]
    assert len(members) == 2
    member_id = [m for m in members if m["role"] == "member"][0]["id"]
    remove = await client.delete(f"/api/v1/household/members/{member_id}", headers=auth["headers"])
    assert remove.status_code == 200
    household2 = await client.get("/api/v1/household", headers=auth["headers"])
    assert len(household2.json()["members"]) == 1


# --- Projections tests ---

@pytest.mark.anyio
async def test_cash_flow_projection(client, auth):
    response = await client.get("/api/v1/projections/cash-flow?months=3", headers=auth["headers"])
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.anyio
async def test_scenario_projection(client, auth):
    response = await client.post(
        "/api/v1/projections/scenario",
        json={"months": 2, "assumptions": {"income_change_pct": 10, "expense_change_pct": -5}},
        headers=auth["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert "months" in data
    assert "projected_net_worth" in data
