import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_refresh_returns_new_refresh_token(client: AsyncClient):
    """After refresh, the new refresh token must be different from the old one."""
    await client.post("/api/v1/auth/register", json={
        "email": "rot1@example.com", "name": "Rot1", "password": "password123",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "rot1@example.com", "password": "password123",
    })
    old_refresh = login.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh,
    })
    assert resp.status_code == 200
    new_refresh = resp.json()["refresh_token"]
    assert new_refresh != old_refresh, "Refresh token must rotate"


@pytest.mark.anyio
async def test_old_refresh_token_becomes_invalid(client: AsyncClient):
    """A refresh token used once must be rejected on second use."""
    await client.post("/api/v1/auth/register", json={
        "email": "rot2@example.com", "name": "Rot2", "password": "password123",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "rot2@example.com", "password": "password123",
    })
    old_refresh = login.json()["refresh_token"]

    # First use — must succeed
    resp1 = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh,
    })
    assert resp1.status_code == 200

    # Second use — must fail
    resp2 = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh,
    })
    assert resp2.status_code == 401


@pytest.mark.anyio
async def test_new_refresh_token_still_works(client: AsyncClient):
    """The token received from a refresh call must be usable for another refresh."""
    await client.post("/api/v1/auth/register", json={
        "email": "rot3@example.com", "name": "Rot3", "password": "password123",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "rot3@example.com", "password": "password123",
    })
    r1 = login.json()["refresh_token"]

    resp1 = await client.post("/api/v1/auth/refresh", json={"refresh_token": r1})
    assert resp1.status_code == 200
    r2 = resp1.json()["refresh_token"]

    resp2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": r2})
    assert resp2.status_code == 200
    r3 = resp2.json()["refresh_token"]
    assert r3 != r2


@pytest.mark.anyio
async def test_multiple_rotations_keep_chain_valid(client: AsyncClient):
    """A chain of 5 rotations must remain valid throughout."""
    await client.post("/api/v1/auth/register", json={
        "email": "rot4@example.com", "name": "Rot4", "password": "password123",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "rot4@example.com", "password": "password123",
    })
    current_refresh = login.json()["refresh_token"]

    for i in range(5):
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": current_refresh,
        })
        assert resp.status_code == 200, f"Rotation {i+1} failed"
        current_refresh = resp.json()["refresh_token"]


@pytest.mark.anyio
async def test_invalid_refresh_token_returns_401(client: AsyncClient):
    """A garbage refresh token must be rejected."""
    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": "not.a.valid.jwt.token",
    })
    assert resp.status_code == 401
