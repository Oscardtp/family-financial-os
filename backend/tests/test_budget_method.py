import pytest
from decimal import Decimal
from pydantic import ValidationError


# ── FASE 6.3B: static preset catalog ────────────────────────────────

class TestMethodPresetsStatic:
    """The catalog lives in the domain. Never persisted as household data."""

    def test_eleven_presets_available(self):
        from app.domain.value_objects.budget_method import list_presets
        presets = list_presets()
        assert len(presets) == 11

    def test_every_preset_sums_to_100(self):
        from app.domain.value_objects.budget_method import list_presets
        for preset in list_presets():
            total = sum(g["pct"] for g in preset["groups"])
            assert total == 100, f"Preset {preset['id']} sums to {total}"

    def test_preset_ids_are_unique(self):
        from app.domain.value_objects.budget_method import list_presets
        ids = [p["id"] for p in list_presets()]
        assert len(ids) == len(set(ids))

    def test_catalog_is_static_between_calls(self):
        from app.domain.value_objects.budget_method import list_presets
        assert list_presets() == list_presets()

    def test_get_preset_unknown_returns_none(self):
        from app.domain.value_objects.budget_method import get_preset
        assert get_preset("no_existe") is None

    def test_get_preset_returns_copy(self):
        from app.domain.value_objects.budget_method import get_preset
        first = get_preset("50_30_20")
        first["groups"].append({"key": "x", "label": "X", "pct": 0})
        assert len(get_preset("50_30_20")["groups"]) == 3


# ── FASE 6.3B: generic engine distribution ──────────────────────────

class TestDistributeByGroups:
    """BudgetEngine.distribute_by_groups is pure: Money in, Money out."""

    def test_n_groups_distribution(self):
        from app.financial_engine.budget_engine import BudgetEngine
        from app.domain.value_objects.money import Money
        result = BudgetEngine().distribute_by_groups(
            Money("5000000"),
            [{"key": "a", "pct": 40}, {"key": "b", "pct": 30}, {"key": "c", "pct": 20}, {"key": "d", "pct": 10}],
        )
        assert result["a"] == Money("2000000")
        assert result["b"] == Money("1500000")
        assert result["c"] == Money("1000000")
        assert result["d"] == Money("500000")

    def test_result_sums_to_income(self):
        from app.financial_engine.budget_engine import BudgetEngine
        from app.domain.value_objects.money import Money
        result = BudgetEngine().distribute_by_groups(
            Money("1000000"),
            [{"key": "a", "pct": 34}, {"key": "b", "pct": 33}, {"key": "c", "pct": 33}],
        )
        total = sum((m.amount for m in result.values()), Decimal("0"))
        assert total == Decimal("1000000.00")

    def test_values_are_money(self):
        from app.financial_engine.budget_engine import BudgetEngine
        from app.domain.value_objects.money import Money
        result = BudgetEngine().distribute_by_groups(
            Money("1000000"), [{"key": "a", "pct": 50}, {"key": "b", "pct": 50}]
        )
        assert all(isinstance(m, Money) for m in result.values())

    def test_bad_sum_raises(self):
        from app.financial_engine.budget_engine import BudgetEngine
        from app.domain.value_objects.money import Money
        with pytest.raises(ValueError):
            BudgetEngine().distribute_by_groups(
                Money("1000000"), [{"key": "a", "pct": 50}, {"key": "b", "pct": 40}]
            )


# ── FASE 6.3B: endpoint tests ───────────────────────────────────────

async def _register(client, email):
    reg = await client.post("/api/v1/auth/register", json={
        "email": email, "name": "Method User", "password": "password123",
    })
    assert reg.status_code == 201
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def _config_payload(**overrides):
    payload = {
        "method_type": "50_30_20",
        "groups": [
            {"key": "necesidades", "label": "Necesidades", "pct": 50},
            {"key": "gustos", "label": "Gustos", "pct": 30},
            {"key": "ahorro", "label": "Ahorro", "pct": 20},
        ],
        "category_groups": {},
        "reference_income_source": "manual",
        "reference_income_amount": "5000000",
    }
    payload.update(overrides)
    return payload


@pytest.mark.anyio
async def test_presets_endpoint(client):
    headers = await _register(client, "presets@example.com")
    response = await client.get("/api/v1/budget-methods/presets", headers=headers)
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) == 11
    for preset in presets:
        assert sum(g["pct"] for g in preset["groups"]) == 100


@pytest.mark.anyio
async def test_config_defaults_when_never_saved(client):
    headers = await _register(client, "defaults@example.com")
    response = await client.get("/api/v1/budget-method", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["method_type"] is None
    assert body["groups"] == []
    assert body["updated_at"] is None


@pytest.mark.anyio
async def test_config_persists_and_returns_updated_at(client):
    headers = await _register(client, "persist@example.com")
    put = await client.put("/api/v1/budget-method", json=_config_payload(), headers=headers)
    assert put.status_code == 200
    assert put.json()["method_type"] == "50_30_20"
    assert put.json()["updated_at"] is not None
    got = await client.get("/api/v1/budget-method", headers=headers)
    assert got.json()["method_type"] == "50_30_20"
    assert got.json()["reference_income_amount"] == "5000000.00"


@pytest.mark.anyio
async def test_config_isolated_per_household(client):
    headers_a = await _register(client, "house_a@example.com")
    headers_b = await _register(client, "house_b@example.com")
    await client.put("/api/v1/budget-method", json=_config_payload(), headers=headers_a)
    got_b = await client.get("/api/v1/budget-method", headers=headers_b)
    assert got_b.json()["method_type"] is None
    got_a = await client.get("/api/v1/budget-method", headers=headers_a)
    assert got_a.json()["method_type"] == "50_30_20"


@pytest.mark.anyio
async def test_config_rejects_sum_not_100(client):
    headers = await _register(client, "badsum@example.com")
    payload = _config_payload(groups=[
        {"key": "necesidades", "label": "Necesidades", "pct": 50},
        {"key": "gustos", "label": "Gustos", "pct": 30},
        {"key": "ahorro", "label": "Ahorro", "pct": 10},
    ])
    response = await client.put("/api/v1/budget-method", json=payload, headers=headers)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_config_rejects_pct_over_100(client):
    headers = await _register(client, "over100@example.com")
    payload = _config_payload(groups=[
        {"key": "todo", "label": "Todo", "pct": 110},
    ])
    response = await client.put("/api/v1/budget-method", json=payload, headers=headers)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_config_rejects_unknown_preset(client):
    headers = await _register(client, "unknown@example.com")
    payload = _config_payload(method_type="99_99_99")
    response = await client.put("/api/v1/budget-method", json=payload, headers=headers)
    assert response.status_code == 400


@pytest.mark.anyio
async def test_preview_returns_backend_computed_amounts(client):
    headers = await _register(client, "preview@example.com")
    response = await client.post("/api/v1/budget-method/preview", json={
        "income_amount": "5000000",
        "groups": [
            {"key": "necesidades", "label": "Necesidades", "pct": 50},
            {"key": "gustos", "label": "Gustos", "pct": 30},
            {"key": "ahorro", "label": "Ahorro", "pct": 20},
        ],
    }, headers=headers)
    assert response.status_code == 200
    body = response.json()
    amounts = {a["key"]: a["amount"] for a in body["allocations"]}
    assert amounts == {
        "necesidades": "2500000.00",
        "gustos": "1500000.00",
        "ahorro": "1000000.00",
    }


@pytest.mark.anyio
async def test_preview_rejects_bad_sum(client):
    headers = await _register(client, "previewbad@example.com")
    response = await client.post("/api/v1/budget-method/preview", json={
        "income_amount": "5000000",
        "groups": [{"key": "todo", "label": "Todo", "pct": 90}],
    }, headers=headers)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_apply_method_never_touches_budgets(client):
    headers = await _register(client, "notouch@example.com")
    cat = await client.post("/api/v1/categories",
        json={"name": "Food", "type": "expense"}, headers=headers)
    cat_id = cat.json()["id"]
    await client.post("/api/v1/budgets", json={
        "category_id": cat_id, "amount": 500000, "month": 1, "year": 2026,
    }, headers=headers)

    before = await client.get("/api/v1/budgets?month=1&year=2026", headers=headers)
    assert len(before.json()) == 1

    put = await client.put("/api/v1/budget-method", json=_config_payload(
        category_groups={cat_id: "necesidades"}
    ), headers=headers)
    assert put.status_code == 200

    after = await client.get("/api/v1/budgets?month=1&year=2026", headers=headers)
    assert len(after.json()) == 1
    assert after.json()[0]["amount"] == before.json()[0]["amount"]


@pytest.mark.anyio
async def test_category_groups_pruned_to_valid_keys(client):
    headers = await _register(client, "prune@example.com")
    put = await client.put("/api/v1/budget-method", json=_config_payload(
        category_groups={"cat-1": "necesidades", "cat-2": "grupo_fantasma"}
    ), headers=headers)
    assert put.status_code == 200
    assert put.json()["category_groups"] == {"cat-1": "necesidades"}


class TestHouseholdMethodConfigSchema:
    """FASE 6.3B — N-group config schema validation (additive, 6.2 intact)."""

    def test_sum_not_100_raises(self):
        from app.presentation.schemas.schemas import HouseholdMethodConfigSchema
        with pytest.raises(ValidationError):
            HouseholdMethodConfigSchema(
                method_type="custom",
                groups=[
                    {"key": "a", "label": "A", "pct": 50},
                    {"key": "b", "label": "B", "pct": 40},
                ],
            )

    def test_method_without_groups_raises(self):
        from app.presentation.schemas.schemas import HouseholdMethodConfigSchema
        with pytest.raises(ValidationError):
            HouseholdMethodConfigSchema(method_type="50_30_20", groups=[])

    def test_empty_config_is_valid(self):
        from app.presentation.schemas.schemas import HouseholdMethodConfigSchema
        config = HouseholdMethodConfigSchema()
        assert config.method_type is None
        assert config.groups == []
