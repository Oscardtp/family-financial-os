"""Tests for authentication and household isolation."""

from __future__ import annotations
import pytest
import os
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.infrastructure.sqlite import init_db, get_connection, get_db_path
from app.domain.domain import User, Household, Session


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
def registered_user(client):
    response = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "household_name": "Test Household"
    })
    assert response.status_code == 201
    return response.json()["data"]


class TestAuth:
    def test_register_creates_user_and_household(self, client):
        response = client.post("/api/v1/auth/register", json={
            "name": "New User",
            "email": "new@example.com",
            "password": "password123",
            "household_name": "New Household"
        })
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["user"]["name"] == "New User"
        assert data["user"]["email"] == "new@example.com"
        assert data["household"]["name"] == "New Household"

    def test_register_duplicate_email_returns_400(self, client, registered_user):
        response = client.post("/api/v1/auth/register", json={
            "name": "Another User",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_returns_session_cookie(self, client, registered_user):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["user"]["email"] == "test@example.com"
        assert "session_id" in response.cookies

    def test_login_invalid_credentials_returns_401(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrong"
        })
        assert response.status_code == 401

    def test_get_me_requires_auth(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_returns_user_info(self, client, registered_user):
        client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["user"]["email"] == "test@example.com"
        assert data["household"]["name"] == "Test Household"

    def test_logout_invalidates_session(self, client, registered_user):
        client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200

        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_protected_route_requires_auth(self, client):
        response = client.get("/api/v1/accounts")
        assert response.status_code == 401

    def test_protected_route_works_with_auth(self, client, registered_user):
        client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        response = client.get("/api/v1/accounts")
        assert response.status_code == 200


class TestHouseholdIsolation:
    def test_different_households_see_different_data(self, client):
        # Register first user
        client.post("/api/v1/auth/register", json={
            "name": "User A",
            "email": "usera@example.com",
            "password": "password123",
            "household_name": "Household A"
        })

        # Register second user
        client.post("/api/v1/auth/register", json={
            "name": "User B",
            "email": "userb@example.com",
            "password": "password123",
            "household_name": "Household B"
        })

        # Login as User A
        client.post("/api/v1/auth/login", json={
            "email": "usera@example.com",
            "password": "password123"
        })

        # Create account for User A
        response = client.post("/api/v1/accounts", json={
            "name": "Account A",
            "type": "bank",
            "initial_balance": "1000.00"
        })
        assert response.status_code == 201

        # Login as User B
        client.post("/api/v1/auth/login", json={
            "email": "userb@example.com",
            "password": "password123"
        })

        # User B should not see User A's account
        response = client.get("/api/v1/accounts")
        assert response.status_code == 200
        accounts = response.json()["data"]
        assert len(accounts) == 0
