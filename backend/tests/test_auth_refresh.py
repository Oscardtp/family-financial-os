"""PHASE 10K — Auth refresh token tests."""
import pytest


# ─── Test 1: Register returns token pair ───
@pytest.mark.anyio
async def test_register_returns_tokens(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "reg_token@test.com", "name": "Reg", "password": "password123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


# ─── Test 2: Login returns token pair ───
@pytest.mark.anyio
async def test_login_returns_tokens(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login_token@test.com", "name": "Login", "password": "password123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login_token@test.com", "password": "password123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


# ─── Test 3: Refresh returns new tokens ───
@pytest.mark.anyio
async def test_refresh_returns_new_tokens(client):
    await client.post("/api/v1/auth/register", json={
        "email": "refresh_new@test.com", "name": "Refresh", "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "refresh_new@test.com", "password": "password123",
    })
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert len(data["access_token"]) > 50
    assert data["refresh_token"] != refresh_token


# ─── Test 4: Refresh token rotation (old token revoked) ───
@pytest.mark.anyio
async def test_refresh_token_rotation(client):
    await client.post("/api/v1/auth/register", json={
        "email": "rotation@test.com", "name": "Rotate", "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "rotation@test.com", "password": "password123",
    })
    old_refresh = login_resp.json()["refresh_token"]

    # First refresh — should succeed
    resp1 = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp1.status_code == 200

    # Second refresh with SAME old token — should fail (revoked)
    resp2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp2.status_code == 401


# ─── Test 5: Invalid refresh token returns 401 ───
@pytest.mark.anyio
async def test_refresh_invalid_token_returns_401(client):
    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid.jwt.token",
    })
    assert resp.status_code == 401


# ─── Test 6: Access token used as refresh returns 401 ───
@pytest.mark.anyio
async def test_refresh_access_token_as_refresh_returns_401(client):
    await client.post("/api/v1/auth/register", json={
        "email": "access_as_refresh@test.com", "name": "AAR", "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "access_as_refresh@test.com", "password": "password123",
    })
    access_token = login_resp.json()["access_token"]

    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": access_token,
    })
    assert resp.status_code == 401


# ─── Test 7: Access token protects /me endpoint ───
@pytest.mark.anyio
async def test_me_requires_access_token(client):
    await client.post("/api/v1/auth/register", json={
        "email": "me_protect@test.com", "name": "ME", "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "me_protect@test.com", "password": "password123",
    })
    access = login_resp.json()["access_token"]

    # Valid access token
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me_protect@test.com"

    # No token — app returns 401 (custom error handler)
    resp2 = await client.get("/api/v1/auth/me")
    assert resp2.status_code in (401, 403)


# ─── Test 8: Refresh with expired token (via fast-forward) ───
@pytest.mark.anyio
async def test_refresh_expired_token_returns_401(client):
    """Expired tokens fail JWT decode (jose validates exp)."""
    # Create a token with 0 expiry by manipulating directly
    from jose import jwt
    from app.config import get_settings
    settings = get_settings()
    expired = jwt.encode(
        {"sub": "fake-user-id", "exp": 0, "type": "refresh", "jti": "fake-jti"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": expired})
    assert resp.status_code == 401


# ─── Test 9: Double refresh rotation chain ───
@pytest.mark.anyio
async def test_double_refresh_rotation_chain(client):
    await client.post("/api/v1/auth/register", json={
        "email": "chain@test.com", "name": "Chain", "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "chain@test.com", "password": "password123",
    })
    token = login_resp.json()["refresh_token"]

    # Chain of 3 refreshes
    for i in range(3):
        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": token})
        assert resp.status_code == 200, f"Refresh chain {i+1} failed"
        token = resp.json()["refresh_token"]


# ─── Test 10: Register then refresh works ───
@pytest.mark.anyio
async def test_register_then_refresh_works(client):
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "reg_refresh@test.com", "name": "RegRef", "password": "password123",
    })
    refresh_token = reg_resp.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


# ─── Test 11: Login then refresh, access token works ───
@pytest.mark.anyio
async def test_login_refresh_then_access_works(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login_ref_access@test.com", "name": "LRA", "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "login_ref_access@test.com", "password": "password123",
    })
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    new_access = refresh_resp.json()["access_token"]

    # Use new access token on /me
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "login_ref_access@test.com"
