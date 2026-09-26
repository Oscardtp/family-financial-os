"""FASE 6.4B (B5) — Fix de /projections/cash-flow.

Antes del fix, el endpoint proyectaba con ceros hardcodeados:
    current_debt_balance=Money(Decimal("0"))
    current_savings=Money(Decimal("0"))
    monthly_debt_payment=Money(Decimal("0"))

Consecuencia: la proyectación de ahorro acumulado ignoraba por completo la
deuda real (no descontaba cuotas) y el ahorro real (empezaba en cero).

Este test replica a mano la fórmula de ProjectionEngine.project_scenario
para congelar el resultado esperado con datos reales.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

EXPECTED_SAVINGS = Decimal("150000")          # aporte real a la meta
EXPECTED_NET_INCOME = Decimal("300000")       # 500.000 ingresos − 200.000 gastos
EXPECTED_MONTHLY_DEBT_PAYMENT = Decimal("100000")   # cuota mínima de la deuda


async def _register(client, email: str) -> dict:
    r = await client.post("/api/v1/auth/register", json={
        "email": email,
        "name": "CashFlow Fix",
        "password": "password123",
    })
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.anyio
async def test_cash_flow_proyecta_deuda_y_ahorro_reales(client):
    headers = await _register(client, "cashflow_fix@example.com")
    today = date.today()

    # 1) cuenta
    r = await client.post("/api/v1/accounts", json={
        "name": "Cuenta cash-flow",
        "type": "bank",
        "balance": "1000000",
    }, headers=headers)
    assert r.status_code == 201, r.text

    # 2) ahorro real: meta + aporte
    r = await client.post("/api/v1/savings/goals", json={
        "name": "Fondo de emergencia",
        "target_amount": "500000",
    }, headers=headers)
    assert r.status_code == 201, r.text
    goal_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/savings/goals/{goal_id}/contributions",
        json={"amount": "150000", "contribution_date": today.isoformat()},
        headers=headers,
    )
    assert r.status_code == 201, r.text

    # 3) deuda real
    r = await client.post("/api/v1/debts", json={
        "name": "Tarjeta cash-flow",
        "total_amount": "1000000",
        "current_balance": "1000000",
        "interest_rate": "2",
        "interest_rate_type": "EM",
        "minimum_payment": "100000",
        "due_day": 31,
    }, headers=headers)
    assert r.status_code == 201, r.text

    # 4) ingresos y gastos del mes en curso
    for tx in (
        {"type": "income", "amount": "500000", "description": "Nómina"},
        {"type": "expense", "amount": "200000", "description": "Mercado"},
    ):
        r = await client.post("/api/v1/transactions", json={
            "account_id": (await client.get("/api/v1/accounts", headers=headers)).json()[0]["id"],
            "type": tx["type"],
            "amount": tx["amount"],
            "description": tx["description"],
            "date": today.isoformat(),
        }, headers=headers)
        assert r.status_code == 201, r.text

    # 5) proyección
    r = await client.get("/api/v1/projections/cash-flow?months=3", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()

    # El fix conserva exactamente 3 claves en la respuesta
    assert set(data.keys()) == {"months", "projections", "projected_savings"}
    assert data["months"] == 3
    assert len(data["projections"]) == 3

    # Fórmula congelada de ProjectionEngine:
    #   ahorro_mes_n = ahorro_inicial + Σ(net_income − cuota_deuda)
    #   cuota_deuda = 100.000 los 3 meses (la deuda no se termina)
    cumulative = []
    running = EXPECTED_SAVINGS
    for _ in range(3):
        running = running + EXPECTED_NET_INCOME - EXPECTED_MONTHLY_DEBT_PAYMENT
        cumulative.append(running)

    for projection, expected in zip(data["projections"], cumulative):
        assert Decimal(projection["cumulative_savings"]) == expected, (
            "la proyección debe descontar la cuota de deuda real y partir "
            "del ahorro real, no de ceros"
        )

    assert Decimal(data["projected_savings"]) == cumulative[-1], (
        "CONGELADO: projected_savings = ahorro real + 3×(net − cuota). "
        "Con los ceros hardcodeados daba 900000 en vez de 750000"
    )

    # ingresos/gastos del mes se proyectan sin cambios
    for projection in data["projections"]:
        assert Decimal(projection["income"]) == Decimal("500000")
        assert Decimal(projection["expenses"]) == Decimal("200000")
        assert Decimal(projection["net_income"]) == EXPECTED_NET_INCOME
