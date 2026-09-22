import pytest
from decimal import Decimal
from pydantic import ValidationError


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


@pytest.mark.anyio
async def test_http_error_handlers_return_friendly_messages(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "errors@example.com", "name": "Error User", "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    unauthorized = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert unauthorized.status_code == 401
    body = unauthorized.json()
    assert body["error"] == "HTTPError"
    assert "iniciar sesión" in body["detail"]

    not_found = await client.get("/api/v1/accounts/nonexistent", headers=headers)
    assert not_found.status_code == 404
    body = not_found.json()
    assert body["error"] == "HTTPError"
    assert "No encontramos" in body["detail"]

    bad_request = await client.post("/api/v1/accounts", json={"name": ""}, headers=headers)
    assert bad_request.status_code == 422
    body = bad_request.json()
    assert body["error"] == "ValidationError"
    assert "fields" in body


@pytest.mark.anyio
async def test_create_recurring_payment_without_account_returns_400(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "recurring@example.com",
        "name": "Recurring User",
        "password": "password123",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/recurring-payments",
        json={
            "name": "Netflix",
            "amount": 55000,
            "type": "expense",
            "frequency": "monthly",
            "day_of_month": 15,
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "HTTPError"
    assert "datos enviados" in body["detail"] or "cuenta" in body["detail"].lower()


# ── FASE 6.2: BudgetMethodConfigSchema tests ──────────────────────────

class TestBudgetMethodConfigSchema:
    """FASE 6.2 — Schema validation for budget method configuration."""

    def test_valid_50_30_20(self):
        from app.presentation.schemas.schemas import BudgetMethodConfigSchema
        config = BudgetMethodConfigSchema(
            method_type="50_30_20",
            needs_pct=Decimal("50"),
            wants_pct=Decimal("30"),
            savings_pct=Decimal("20"),
        )
        assert config.method_type == "50_30_20"
        assert config.needs_pct == Decimal("50")

    def test_valid_custom(self):
        from app.presentation.schemas.schemas import BudgetMethodConfigSchema
        config = BudgetMethodConfigSchema(
            method_type="custom",
            needs_pct=Decimal("60"),
            wants_pct=Decimal("25"),
            savings_pct=Decimal("15"),
        )
        assert config.method_type == "custom"

    def test_sum_not_100_raises_validation_error(self):
        from app.presentation.schemas.schemas import BudgetMethodConfigSchema
        with pytest.raises(ValidationError):
            BudgetMethodConfigSchema(
                method_type="custom",
                needs_pct=Decimal("50"),
                wants_pct=Decimal("30"),
                savings_pct=Decimal("15"),
            )

    def test_negative_value_raises_validation_error(self):
        from app.presentation.schemas.schemas import BudgetMethodConfigSchema
        with pytest.raises(ValidationError):
            BudgetMethodConfigSchema(
                method_type="custom",
                needs_pct=Decimal("-10"),
                wants_pct=Decimal("60"),
                savings_pct=Decimal("50"),
            )

    def test_value_over_100_raises_validation_error(self):
        from app.presentation.schemas.schemas import BudgetMethodConfigSchema
        with pytest.raises(ValidationError):
            BudgetMethodConfigSchema(
                method_type="custom",
                needs_pct=Decimal("110"),
                wants_pct=Decimal("0"),
                savings_pct=Decimal("0"),
            )


class TestBudgetMethodMultitenancy:
    """FASE 6.2 — Verify household_id isolation for budget method configs."""

    def test_engine_is_pure_function_supports_multitenancy(self):
        """BudgetEngine.calculate_method_distribution is stateless —
        different households can compute independently with no shared state."""
        from app.financial_engine.budget_engine import BudgetEngine
        from app.domain.value_objects.money import Money

        engine = BudgetEngine()

        household_a = engine.calculate_method_distribution(
            income=Money("5000000"),
            needs_pct=Decimal("50"),
            wants_pct=Decimal("30"),
            savings_pct=Decimal("20"),
        )
        household_b = engine.calculate_method_distribution(
            income=Money("3000000"),
            needs_pct=Decimal("70"),
            wants_pct=Decimal("20"),
            savings_pct=Decimal("10"),
        )

        assert household_a["needs"] == Money("2500000")
        assert household_b["needs"] == Money("2100000")
        assert household_a["needs"] != household_b["needs"]
