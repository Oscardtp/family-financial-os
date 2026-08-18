"""Integration tests for Family Financial OS API."""

from __future__ import annotations
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.infrastructure.sqlite import init_db, get_connection, get_db_path
import os


@pytest.fixture(autouse=True)
def setup_db():
    db_path = get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    yield
    try:
        conn = get_connection()
        conn.execute("DELETE FROM households")
        conn.commit()
        conn.close()
    except Exception:
        pass
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authenticated_client(client):
    client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "household_name": "Test Household"
    })
    client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    return client


class TestAccountAPI:
    def test_create_account(self, authenticated_client):
        response = authenticated_client.post("/api/v1/accounts", json={
            "name": "Cuenta Principal",
            "type": "bank",
            "initial_balance": "1000000.00"
        })
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Cuenta Principal"
        assert data["balance"] == "1000000.00"

    def test_list_accounts(self, authenticated_client):
        authenticated_client.post("/api/v1/accounts", json={
            "name": "Cuenta 1",
            "type": "bank",
            "initial_balance": "500000.00"
        })
        authenticated_client.post("/api/v1/accounts", json={
            "name": "Cuenta 2",
            "type": "digital_wallet",
            "initial_balance": "100000.00"
        })
        response = authenticated_client.get("/api/v1/accounts")
        assert response.status_code == 200
        accounts = response.json()["data"]
        assert len(accounts) == 2

    def test_get_account(self, authenticated_client):
        create_response = authenticated_client.post("/api/v1/accounts", json={
            "name": "Test Account",
            "type": "bank",
            "initial_balance": "250000.00"
        })
        account_id = create_response.json()["data"]["id"]
        response = authenticated_client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Test Account"

    def test_delete_account(self, authenticated_client):
        create_response = authenticated_client.post("/api/v1/accounts", json={
            "name": "To Delete",
            "type": "bank",
            "initial_balance": "0.00"
        })
        account_id = create_response.json()["data"]["id"]
        response = authenticated_client.delete(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 204
        response = authenticated_client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 404


class TestTransactionAPI:
    def test_create_income(self, authenticated_client):
        account = authenticated_client.post("/api/v1/accounts", json={
            "name": "Income Account",
            "type": "bank",
            "initial_balance": "0.00"
        }).json()["data"]
        category = authenticated_client.post("/api/v1/categories", json={
            "name": "Salario",
            "type": "income"
        }).json()["data"]
        response = authenticated_client.post("/api/v1/transactions", json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "income",
            "amount": "3000000.00",
            "description": "Pago mensual"
        })
        assert response.status_code == 201

    def test_create_expense(self, authenticated_client):
        account = authenticated_client.post("/api/v1/accounts", json={
            "name": "Expense Account",
            "type": "bank",
            "initial_balance": "1000000.00"
        }).json()["data"]
        category = authenticated_client.post("/api/v1/categories", json={
            "name": "Mercado",
            "type": "expense"
        }).json()["data"]
        response = authenticated_client.post("/api/v1/transactions", json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "expense",
            "amount": "50000.00",
            "description": "Compra supermercado"
        })
        assert response.status_code == 201

    def test_list_transactions(self, authenticated_client):
        response = authenticated_client.get("/api/v1/transactions")
        assert response.status_code == 200
        assert "data" in response.json()

    def test_transaction_filters(self, authenticated_client):
        response = authenticated_client.get("/api/v1/transactions?type=income")
        assert response.status_code == 200


class TestTransferAPI:
    def test_create_transfer(self, authenticated_client):
        source = authenticated_client.post("/api/v1/accounts", json={
            "name": "Source",
            "type": "bank",
            "initial_balance": "500000.00"
        }).json()["data"]
        dest = authenticated_client.post("/api/v1/accounts", json={
            "name": "Destination",
            "type": "digital_wallet",
            "initial_balance": "0.00"
        }).json()["data"]
        response = authenticated_client.post("/api/v1/transfers", json={
            "from_account_id": source["id"],
            "to_account_id": dest["id"],
            "amount": "100000.00",
            "description": "Test transfer"
        })
        assert response.status_code == 201

    def test_list_transfers(self, authenticated_client):
        response = authenticated_client.get("/api/v1/transfers")
        assert response.status_code == 200
        assert "data" in response.json()


class TestHouseholdAPI:
    def test_get_household(self, authenticated_client):
        response = authenticated_client.get("/api/v1/household")
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Test Household"

    def test_update_household(self, authenticated_client):
        response = authenticated_client.put("/api/v1/household", json={
            "name": "Updated Household"
        })
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Updated Household"


class TestMemberAPI:
    def test_create_member(self, authenticated_client):
        response = authenticated_client.post("/api/v1/members", json={
            "name": "Test Member",
            "role": "adult"
        })
        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Test Member"

    def test_list_members(self, authenticated_client):
        authenticated_client.post("/api/v1/members", json={"name": "Member 1", "role": "adult"})
        response = authenticated_client.get("/api/v1/members")
        assert response.status_code == 200
        assert len(response.json()["data"]) >= 1


class TestCategoryAPI:
    def test_create_category(self, authenticated_client):
        response = authenticated_client.post("/api/v1/categories", json={
            "name": "Test Category",
            "type": "expense"
        })
        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Test Category"

    def test_list_categories(self, authenticated_client):
        authenticated_client.post("/api/v1/categories", json={
            "name": "Cat 1", "type": "expense"
        })
        response = authenticated_client.get("/api/v1/categories")
        assert response.status_code == 200
        assert len(response.json()["data"]) >= 1


class TestSmokeAPI:
    def test_quick_expense(self, authenticated_client):
        account = authenticated_client.post("/api/v1/accounts", json={
            "name": "Quick Account",
            "type": "bank",
            "initial_balance": "1000000.00"
        }).json()["data"]
        category = authenticated_client.post("/api/v1/categories", json={
            "name": "Comida", "type": "expense"
        }).json()["data"]
        response = authenticated_client.post("/api/v1/transactions/quick", json={
            "amount": "25000.00",
            "category_id": category["id"],
            "account_id": account["id"]
        })
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["amount"] == "25000.00"
        assert data["type"] == "expense"

    def test_dashboard(self, authenticated_client):
        response = authenticated_client.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "summary" in data
        assert "cash_flow" in data
        assert "upcoming_payments" in data
        assert isinstance(data["cash_flow"], list)
        assert isinstance(data["upcoming_payments"], list)

    def test_categories_tree(self, authenticated_client):
        authenticated_client.post("/api/v1/categories", json={
            "name": "Root", "type": "expense"
        })
        response = authenticated_client.get("/api/v1/categories/tree")
        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)

    def test_transfer_list(self, authenticated_client):
        response = authenticated_client.get("/api/v1/transfers")
        assert response.status_code == 200
        assert "data" in response.json()
