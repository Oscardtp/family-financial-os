import pytest
from datetime import date
from decimal import Decimal


# ─── TransactionService ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_transaction_service_create_income(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_tx_income@example.com", "name": "Svc TX", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 0}, headers=headers)
    acc_id = acc.json()["id"]

    resp = await client.post("/api/v1/transactions", json={
        "account_id": acc_id, "type": "income", "amount": 5000,
        "description": "Salary", "date": "2026-01-15",
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["type"] == "income"

    acc_resp = await client.get(f"/api/v1/accounts/{acc_id}", headers=headers)
    assert float(acc_resp.json()["balance"]) == 5000.0


@pytest.mark.anyio
async def test_transaction_service_create_expense(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_tx_expense@example.com", "name": "Svc Exp", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 10000}, headers=headers)
    acc_id = acc.json()["id"]

    resp = await client.post("/api/v1/transactions", json={
        "account_id": acc_id, "type": "expense", "amount": 2000,
        "description": "Rent", "date": "2026-01-15",
    }, headers=headers)
    assert resp.status_code == 201

    acc_resp = await client.get(f"/api/v1/accounts/{acc_id}", headers=headers)
    assert float(acc_resp.json()["balance"]) == 8000.0


@pytest.mark.anyio
async def test_transaction_service_insufficient_funds(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_tx_nofunds@example.com", "name": "No Funds", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 100}, headers=headers)
    acc_id = acc.json()["id"]

    resp = await client.post("/api/v1/transactions", json={
        "account_id": acc_id, "type": "expense", "amount": 500,
        "description": "Expensive", "date": "2026-01-15",
    }, headers=headers)
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_transaction_service_create_transfer(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_tx_transfer@example.com", "name": "Transfer", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc1 = await client.post("/api/v1/accounts",
        json={"name": "A", "type": "bank", "balance": 5000}, headers=headers)
    acc2 = await client.post("/api/v1/accounts",
        json={"name": "B", "type": "bank", "balance": 1000}, headers=headers)

    resp = await client.post("/api/v1/transactions", json={
        "account_id": acc1.json()["id"], "type": "transfer", "amount": 2000,
        "to_account_id": acc2.json()["id"], "description": "Move money",
        "date": "2026-01-15",
    }, headers=headers)
    assert resp.status_code == 201

    a1 = await client.get(f"/api/v1/accounts/{acc1.json()['id']}", headers=headers)
    a2 = await client.get(f"/api/v1/accounts/{acc2.json()['id']}", headers=headers)
    assert float(a1.json()["balance"]) == 3000.0
    assert float(a2.json()["balance"]) == 3000.0


@pytest.mark.anyio
async def test_transaction_service_delete_reverses(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_tx_del@example.com", "name": "Del TX", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 0}, headers=headers)
    acc_id = acc.json()["id"]

    tx = await client.post("/api/v1/transactions", json={
        "account_id": acc_id, "type": "income", "amount": 3000,
        "description": "Freelance", "date": "2026-01-15",
    }, headers=headers)
    tx_id = tx.json()["id"]

    resp = await client.delete(f"/api/v1/transactions/{tx_id}", headers=headers)
    assert resp.status_code == 204

    acc_resp = await client.get(f"/api/v1/accounts/{acc_id}", headers=headers)
    assert float(acc_resp.json()["balance"]) == 0.0


# ─── DebtService ──────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_debt_service_create_and_list(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_debt@example.com", "name": "Debt Svc", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    resp = await client.post("/api/v1/debts", json={
        "name": "Credit Card", "creditor": "Banco",
        "total_amount": 5000000, "current_balance": 3000000,
        "interest_rate": 24.0, "minimum_payment": 150000,
        "due_day": 15, "start_date": "2026-01-01",
    }, headers=headers)
    assert resp.status_code == 201
    debt_id = resp.json()["id"]

    list_resp = await client.get("/api/v1/debts", headers=headers)
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id"] == debt_id


@pytest.mark.anyio
async def test_debt_service_payment_interest_split(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_debt_pay@example.com", "name": "Debt Pay", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    debt = await client.post("/api/v1/debts", json={
        "name": "Loan", "creditor": "Bank",
        "total_amount": 1000000, "current_balance": 1000000,
        "interest_rate": 12.0, "minimum_payment": 100000,
        "due_day": 1, "start_date": "2026-01-01",
    }, headers=headers)
    debt_id = debt.json()["id"]

    resp = await client.post(f"/api/v1/debts/{debt_id}/payments", json={
        "amount": 200000, "payment_date": "2026-02-01",
    }, headers=headers)
    assert resp.status_code == 201
    payment = resp.json()
    assert float(payment["interest"]) > 0
    assert float(payment["principal"]) > 0


@pytest.mark.anyio
async def test_debt_service_toggle(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_debt_toggle@example.com", "name": "Toggle", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    debt = await client.post("/api/v1/debts", json={
        "name": "Loan", "creditor": "Bank",
        "total_amount": 100000, "current_balance": 100000,
        "interest_rate": 10.0, "minimum_payment": 10000,
        "due_day": 1, "start_date": "2026-01-01",
    }, headers=headers)
    debt_id = debt.json()["id"]
    assert debt.json()["status"] == "active"

    resp = await client.post(f"/api/v1/debts/{debt_id}/toggle", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "paused"

    resp2 = await client.post(f"/api/v1/debts/{debt_id}/toggle", headers=headers)
    assert resp2.json()["status"] == "active"


# ─── RecurringPaymentService ──────────────────────────────────────────

@pytest.mark.anyio
async def test_recurring_payment_service_create_and_pay(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_recurring@example.com", "name": "Recurring", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 50000}, headers=headers)

    rp = await client.post("/api/v1/recurring-payments", json={
        "account_id": acc.json()["id"], "name": "Netflix",
        "amount": 45000, "type": "expense", "frequency": "monthly",
        "day_of_month": 15, "next_due_date": "2026-03-15",
    }, headers=headers)
    assert rp.status_code == 201
    rp_id = rp.json()["id"]

    resp = await client.post(f"/api/v1/recurring-payments/{rp_id}/pay", headers=headers)
    assert resp.status_code == 200

    acc_resp = await client.get(f"/api/v1/accounts/{acc.json()['id']}", headers=headers)
    assert float(acc_resp.json()["balance"]) == 5000.0


@pytest.mark.anyio
async def test_recurring_payment_service_calculates_next_due(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_recurring_next@example.com", "name": "Next Due", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 100000}, headers=headers)

    rp = await client.post("/api/v1/recurring-payments", json={
        "account_id": acc.json()["id"], "name": "Gym",
        "amount": 80000, "type": "expense", "frequency": "monthly",
        "day_of_month": 1, "next_due_date": "2026-03-01",
    }, headers=headers)
    rp_id = rp.json()["id"]
    old_next = rp.json()["next_due_date"]

    await client.post(f"/api/v1/recurring-payments/{rp_id}/pay", headers=headers)

    updated = await client.get(f"/api/v1/recurring-payments/{rp_id}", headers=headers)
    assert updated.json()["next_due_date"] != old_next


# ─── BudgetService ────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_budget_service_duplicate_rejected(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_budget@example.com", "name": "Budget", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    cat = await client.post("/api/v1/categories",
        json={"name": "Food", "type": "expense", "icon": "🍎", "color": "#ef4444"},
        headers=headers)
    cat_id = cat.json()["id"]

    await client.post("/api/v1/budgets", json={
        "category_id": cat_id, "amount": 500000, "month": 1, "year": 2026,
    }, headers=headers)

    resp = await client.post("/api/v1/budgets", json={
        "category_id": cat_id, "amount": 600000, "month": 1, "year": 2026,
    }, headers=headers)
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_budget_service_status(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_budget_status@example.com", "name": "Budget Status", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 1000000}, headers=headers)
    cat = await client.post("/api/v1/categories",
        json={"name": "Food", "type": "expense", "icon": "🍎", "color": "#ef4444"},
        headers=headers)

    await client.post("/api/v1/budgets", json={
        "category_id": cat.json()["id"], "amount": 500000, "month": 1, "year": 2026,
    }, headers=headers)

    await client.post("/api/v1/transactions", json={
        "account_id": acc.json()["id"], "category_id": cat.json()["id"],
        "type": "expense", "amount": 300000, "description": "Groceries",
        "date": "2026-01-15",
    }, headers=headers)

    resp = await client.get("/api/v1/budgets/status?month=1&year=2026", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "ok"


# ─── SavingsService ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_savings_service_contribution_updates_amount(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_savings@example.com", "name": "Savings", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    goal = await client.post("/api/v1/savings/goals", json={
        "name": "Emergency Fund", "target_amount": 5000000,
        "target_date": "2026-12-31",
        "monthly_contribution": 500000, "priority": "high", "goal_type": "savings",
    }, headers=headers)
    goal_id = goal.json()["id"]
    assert float(goal.json()["current_amount"]) == 0.0

    resp = await client.post(f"/api/v1/savings/goals/{goal_id}/contributions", json={
        "amount": 250000, "contribution_date": "2026-02-01",
    }, headers=headers)
    assert resp.status_code == 201

    updated = await client.get(f"/api/v1/savings/goals/{goal_id}", headers=headers)
    assert float(updated.json()["current_amount"]) == 250000.0

    resp2 = await client.post(f"/api/v1/savings/goals/{goal_id}/contributions", json={
        "amount": 750000, "contribution_date": "2026-03-01",
    }, headers=headers)
    assert resp2.status_code == 201

    updated2 = await client.get(f"/api/v1/savings/goals/{goal_id}", headers=headers)
    assert float(updated2.json()["current_amount"]) == 1000000.0


@pytest.mark.anyio
async def test_savings_service_summary(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_savings_sum@example.com", "name": "Sum", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 100000}, headers=headers)

    await client.post("/api/v1/savings/goals", json={
        "name": "Trip", "target_amount": 2000000,
        "monthly_contribution": 200000,
        "priority": "medium", "goal_type": "savings",
    }, headers=headers)

    today = date.today()
    today_str = today.isoformat()

    await client.post("/api/v1/transactions", json={
        "account_id": acc.json()["id"], "type": "income",
        "amount": 3000000, "description": "Salary", "date": today_str,
    }, headers=headers)
    await client.post("/api/v1/transactions", json={
        "account_id": acc.json()["id"], "type": "expense",
        "amount": 2000000, "description": "Living", "date": today_str,
    }, headers=headers)

    resp = await client.get("/api/v1/savings/summary", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_current"] == 0.0
    assert data["savings_rate"] is not None


# ─── DashboardService ─────────────────────────────────────────────────

@pytest.mark.anyio
async def test_dashboard_service_summary(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_dash@example.com", "name": "Dash", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 100000}, headers=headers)

    today = date.today()
    today_str = today.isoformat()

    await client.post("/api/v1/transactions", json={
        "account_id": acc.json()["id"], "type": "income",
        "amount": 5000000, "description": "Salary", "date": today_str,
    }, headers=headers)

    resp = await client.get("/api/v1/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["total_balance"]) == 5100000.0
    assert float(data["monthly_income"]) == 5000000.0


@pytest.mark.anyio
async def test_dashboard_service_financial_alert(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_dash_alert@example.com", "name": "Alert", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 100000}, headers=headers)

    today = date.today()
    today_str = today.isoformat()

    await client.post("/api/v1/transactions", json={
        "account_id": acc.json()["id"], "type": "income",
        "amount": 1000000, "description": "Salary", "date": today_str,
    }, headers=headers)

    await client.post("/api/v1/debts", json={
        "name": "Big Debt", "creditor": "Bank",
        "total_amount": 5000000, "current_balance": 5000000,
        "interest_rate": 24.0, "minimum_payment": 2000000,
        "due_day": today.day, "start_date": today_str,
    }, headers=headers)

    resp = await client.get("/api/v1/dashboard", headers=headers)
    data = resp.json()
    assert data["financial_alert"] is not None
    assert data["financial_alert"]["type"] in ("critical", "warning")


# ─── Validaciones dominio FASE 3 ─────────────────────────────────────

@pytest.mark.anyio
async def test_transaction_service_rejects_zero_amount(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_tx_zero@example.com", "name": "Zero TX", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    acc = await client.post("/api/v1/accounts",
        json={"name": "Checking", "type": "bank", "balance": 1000}, headers=headers)
    acc_id = acc.json()["id"]

    resp = await client.post("/api/v1/transactions", json={
        "account_id": acc_id, "type": "income", "amount": 0,
        "description": "Bad", "date": "2026-01-15",
    }, headers=headers)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_debt_service_create_validates_domain_rules(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_debt_val@example.com", "name": "Debt Val", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    resp = await client.post("/api/v1/debts", json={
        "name": "Bad", "creditor": "Bank",
        "total_amount": 0, "current_balance": 0,
        "interest_rate": -1, "minimum_payment": -100,
        "due_day": 1, "start_date": "2026-01-01",
    }, headers=headers)
    assert resp.status_code == 422

    resp2 = await client.post("/api/v1/debts", json={
        "name": "Bad", "creditor": "Bank",
        "total_amount": 1000, "current_balance": 2000,
        "interest_rate": 10, "minimum_payment": 100,
        "due_day": 1, "start_date": "2026-01-01",
    }, headers=headers)
    assert resp2.status_code == 400


@pytest.mark.anyio
async def test_debt_service_payment_rejects_zero_amount(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "svc_debt_pay_zero@example.com", "name": "Pay Zero", "password": "password123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    debt = await client.post("/api/v1/debts", json={
        "name": "Loan", "creditor": "Bank",
        "total_amount": 1000000, "current_balance": 1000000,
        "interest_rate": 12.0, "minimum_payment": 100000,
        "due_day": 1, "start_date": "2026-01-01",
    }, headers=headers)
    debt_id = debt.json()["id"]

    resp = await client.post(f"/api/v1/debts/{debt_id}/payments", json={
        "amount": 0, "payment_date": "2026-02-01",
    }, headers=headers)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_debt_service_create_validates_domain_rules_unit(session):
    from app.application.services.debt_service import DebtService
    from app.presentation.schemas.schemas import DebtCreate

    service = DebtService(session)
    bad = DebtCreate(
        name="Bad", creditor="Bank",
        total_amount=1000, current_balance=1000,
        interest_rate=10, minimum_payment=100,
        due_day=1, start_date="2026-01-01",
    )
    bad.current_balance = 2000
    with pytest.raises(ValueError):
        await service.create(bad, str(__import__('uuid').uuid4()))


@pytest.mark.anyio
async def test_debt_service_payment_validates_amount_unit(session):
    from app.application.services.debt_service import DebtService
    from app.presentation.schemas.schemas import DebtPaymentCreate
    from app.infrastructure.models.models import DebtModel
    from uuid import uuid4
    from datetime import date

    service = DebtService(session)
    household_id = str(uuid4())
    debt = DebtModel(
        household_id=household_id,
        name="Loan",
        creditor="Bank",
        total_amount=1000000,
        current_balance=1000000,
        interest_rate=12,
        minimum_payment=100000,
        due_day=1,
        start_date=date(2026, 1, 1),
    )
    session.add(debt)
    await session.flush()

    payment_data = DebtPaymentCreate(amount=1000, payment_date=date(2026, 2, 1))
    payment_data.amount = 0
    with pytest.raises(ValueError):
        await service.create_payment(str(debt.id), payment_data, {"household_id": household_id, "id": str(uuid4())})
