"""FASE 6.4B — Characterization Tests (Core Financial Freeze).

Congela el comportamiento ACTUAL del Core Financiero antes de cualquier refactor.

IMPORTANTE:
  Estos tests NO validan que el comportamiento sea "correcto".
  Lo documentan tal como funciona hoy, INCLUDING los defectos conocidos
  (auditoría 6.4A, hallazgos G-1, D-2, D-3, D-4, D-5).

  Si uno de estos tests falla tras un refactor de 6.4C/6.4D/6.4E,
  el comportamiento del sistema CAMBIÓ y hay que justificarlo explícitamente.

Flujos congelados:
  Flujo 1 — Crear deuda        (deuda → obligación → 12 eventos)
  Flujo 2 — Pago de deuda      (POST /debts/{id}/payments)
  Flujo 3 — Pago desde evento  (POST /events/{id}/pay sobre evento de deuda)
  Flujo 4 — Pago recurrente    (POST /events/{id}/pay sobre evento recurrente)

Datos usados (deterministas):
  saldo 1.000.000 · tasa 2% EM → interés mensual = 20.000,00 exactos
  cuota mínima 100.000 → principal 80.000,00 → saldo 920.000,00
  due_day = 31 → la primera ocurrencia SIEMPRE cae en el mes en curso
"""
from __future__ import annotations

from calendar import monthrange
from datetime import date

import pytest

BALANCE = "1000000.00"
INTEREST = "20000.00"        # 1.000.000 × 2% EM
PRINCIPAL = "80000.00"       # 100.000 − 20.000
NEW_BALANCE = "920000.00"    # 1.000.000 − 80.000
MIN_PAYMENT = "100000.00"
RECURRING_AMOUNT = "45000.00"


# ---------------------------------------------------------------- helpers

async def _register(client, email: str) -> dict:
    r = await client.post("/api/v1/auth/register", json={
        "email": email,
        "name": "Characterization",
        "password": "password123",
    })
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _create_debt(client, headers: dict, **overrides) -> dict:
    payload = {
        "name": "Deuda caracterización",
        "creditor": "Banco Test",
        "total_amount": BALANCE,
        "current_balance": BALANCE,
        "interest_rate": "2",
        "interest_rate_type": "EM",
        "minimum_payment": MIN_PAYMENT,
        "due_day": 31,
    }
    payload.update(overrides)
    r = await client.post("/api/v1/debts", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def _event_window() -> tuple[date, date]:
    """Ventana segura para leer los 12 eventos generados (mes actual + 14)."""
    today = date.today()
    start = date(today.year, today.month, 1)
    total = today.year * 12 + (today.month - 1) + 14
    return start, date(total // 12, total % 12 + 1, 1)


async def _get_events(client, headers: dict, date_from: date, date_to: date) -> list[dict]:
    r = await client.get(
        "/api/v1/events",
        params={"from_date": date_from.isoformat(), "to_date": date_to.isoformat()},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


async def _current_month_events(client, headers: dict) -> list[dict]:
    today = date.today()
    start = date(today.year, today.month, 1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1)
    else:
        end = date(today.year, today.month + 1, 1)
    return await _get_events(client, headers, start, end)


async def _debt_obligation(client, headers: dict, debt_id: str) -> dict:
    r = await client.get("/api/v1/obligations", headers=headers)
    assert r.status_code == 200, r.text
    matches = [
        o for o in r.json()
        if o.get("source") == "SYSTEM" and o.get("source_id") == debt_id
    ]
    assert len(matches) == 1, f"esperaba 1 obligación SYSTEM para la deuda, hay {len(matches)}"
    return matches[0]


async def _get_transactions(client, headers: dict) -> list[dict]:
    r = await client.get("/api/v1/transactions", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


async def _create_account(client, headers: dict, balance: str = "1000000") -> dict:
    r = await client.post("/api/v1/accounts", json={
        "name": "Cuenta caracterización",
        "type": "bank",
        "balance": balance,
    }, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------- Flujo 1

@pytest.mark.anyio
async def test_flujo1_crear_deuda_genera_obligacion_y_12_eventos(client):
    """FLUJO 1 (congelado): crear deuda → obligación derivada → 12 eventos."""
    headers = await _register(client, "char_flow1@example.com")
    debt = await _create_debt(client, headers)

    # 1) Deuda creada
    assert debt["current_balance"] == BALANCE
    assert debt["total_amount"] == BALANCE
    assert debt["minimum_payment"] == MIN_PAYMENT
    assert debt["interest_rate"] == "2.00"   # cuantizado a 2 decimales
    assert debt["interest_rate_type"] == "EM"
    assert debt["due_day"] == 31
    assert debt["status"] == "active"

    # 2) Obligación derivada (espejo SYSTEM)
    ob = await _debt_obligation(client, headers, debt["id"])
    assert ob["type"] == "debt"
    assert ob["amount"] == MIN_PAYMENT          # copia literal de minimum_payment
    assert ob["anchor_day"] == debt["due_day"]  # copia literal de due_day
    assert ob["frequency"] == "monthly"
    assert ob["currency"] == "COP"
    assert ob["is_active"] is True
    assert ob["confidence"] == 100
    assert ob["reminder_days_before"] == 3
    assert ob["recommended_offset_days"] == 5

    # 3) 12 eventos generados
    start, end = _event_window()
    events = await _get_events(client, headers, start, end)
    events = [e for e in events if e.get("obligation_id") == ob["id"]]
    assert len(events) == 12, f"esperaba 12 eventos, hay {len(events)}"

    today = date.today()
    first_due = date(today.year, today.month, min(31, monthrange(today.year, today.month)[1]))
    assert events[0]["due_date"] == first_due.isoformat(), (
        "la primera cuota debe caer en el mes en curso cuando due_day = 31"
    )

    for ev in events:
        assert ev["status"] == "pending"
        assert ev["is_recurrent"] is True
        assert ev["type"] == "debt"
        assert ev["amount"] == MIN_PAYMENT
        assert ev["source"] == "SYSTEM"
        assert ev["recurrence_group_id"] == ob["id"]
        assert ev["visibility"] == "estimated"
        assert ev["reminder_days_before"] == 3
        assert ev["account_id"] is None   # la deuda no arrastra cuenta contable

    # 4) Crear deuda NO mueve dinero: cero transacciones
    txs = await _get_transactions(client, headers)
    assert txs == [], "crear una deuda no debe crear transacciones"


# ---------------------------------------------------------------- Flujo 2

@pytest.mark.anyio
async def test_flujo2_pago_por_monto_registra_interes_principal_saldo_y_evento(client):
    """FLUJO 2 (congelado): POST /debts/{id}/payments."""
    headers = await _register(client, "char_flow2@example.com")
    debt = await _create_debt(client, headers)
    today = date.today()

    r = await client.post(
        f"/api/v1/debts/{debt['id']}/payments",
        json={"amount": MIN_PAYMENT, "payment_date": today.isoformat()},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    payment = r.json()

    # interés / principal / monto
    assert payment["amount"] == MIN_PAYMENT
    assert payment["interest"] == INTEREST
    assert payment["principal"] == PRINCIPAL
    assert payment["payment_date"] == today.isoformat()
    assert payment["is_reversed"] is False

    # saldo
    r = await client.get(f"/api/v1/debts/{debt['id']}", headers=headers)
    assert r.status_code == 200
    assert r.json()["current_balance"] == NEW_BALANCE
    assert r.json()["status"] == "active"

    # evento del mes marcado como pagado
    events = await _current_month_events(client, headers)
    ev = next(e for e in events if e.get("obligation_id"))
    assert ev["status"] == "paid"
    assert ev["paid_amount"] == MIN_PAYMENT
    assert ev["paid_by"] is None, "pago por monto no registra quién pagó"

    # historial de pagos
    r = await client.get(f"/api/v1/debts/{debt['id']}/payments", headers=headers)
    assert len(r.json()) == 1


@pytest.mark.anyio
async def test_flujo2_pago_por_monto_no_crea_transaccion(client):
    """DEFECTO CONGELADO (G-1): pagar la deuda no genera Transaction."""
    headers = await _register(client, "char_flow2b@example.com")
    debt = await _create_debt(client, headers)

    r = await client.post(
        f"/api/v1/debts/{debt['id']}/payments",
        json={"amount": MIN_PAYMENT, "payment_date": date.today().isoformat()},
        headers=headers,
    )
    assert r.status_code == 201, r.text

    txs = await _get_transactions(client, headers)
    assert txs == [], (
        "CONGELADO: hoy el pago de deuda NO crea transacción → no afecta "
        "saldo de cuenta, cashflow ni presupuesto (hallazgo G-1 de 6.4A)"
    )


# ---------------------------------------------------------------- Flujo 3

@pytest.mark.anyio
async def test_flujo3_pago_desde_evento_usa_misma_matematica(client):
    """FLUJO 3 (congelado): POST /events/{id}/pay sobre un evento de deuda."""
    headers = await _register(client, "char_flow3@example.com")
    debt = await _create_debt(client, headers)

    events = await _current_month_events(client, headers)
    debt_events = [e for e in events if e.get("obligation_id")]
    assert len(debt_events) == 1
    event = debt_events[0]
    assert event["status"] == "pending"
    assert event["amount"] == MIN_PAYMENT

    r = await client.post(f"/api/v1/events/{event['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text
    paid_event = r.json()
    assert paid_event["status"] == "paid"
    assert paid_event["paid_amount"] == MIN_PAYMENT
    assert paid_event["paid_by"] is not None, "pago desde evento SÍ registra quién pagó"

    # misma matemática que el Flujo 2
    r = await client.get(f"/api/v1/debts/{debt['id']}", headers=headers)
    assert r.json()["current_balance"] == NEW_BALANCE

    r = await client.get(f"/api/v1/debts/{debt['id']}/payments", headers=headers)
    payments = r.json()
    assert len(payments) == 1
    assert payments[0]["interest"] == INTEREST
    assert payments[0]["principal"] == PRINCIPAL
    # fecha de pago = fecha de vencimiento del evento (no la fecha elegida por el usuario)
    assert payments[0]["payment_date"] == event["due_date"]


@pytest.mark.anyio
async def test_flujo3_pago_desde_evento_tampoco_crea_transaccion(client):
    """DEFECTO CONGELADO: el evento de deuda tampoco genera Transaction.

    event_service._create_transaction_for_recurring_event resuelve el
    RecurringPayment por obligation.source_id; para deudas ese id es un
    DebtModel, el lookup devuelve None y sale sin crear transacción.
    """
    headers = await _register(client, "char_flow3b@example.com")
    await _create_debt(client, headers)

    events = await _current_month_events(client, headers)
    event = next(e for e in events if e.get("obligation_id"))

    r = await client.post(f"/api/v1/events/{event['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text

    txs = await _get_transactions(client, headers)
    assert txs == [], (
        "CONGELADO: pagar un evento de deuda NO crea transacción (hallazgo G-1)"
    )


@pytest.mark.anyio
async def test_flujo2_vs_flujo3_diferencias_documentadas(client):
    """Evidencia explícita de las diferencias entre Flujo 2 y Flujo 3.

    Matemática idéntica; difieren en la fecha del pago y en quién queda
    registrado como pagador en el evento.
    """
    today = date.today()

    # --- Flujo 2 (pago por monto), hogar A
    headers_a = await _register(client, "char_diff_a@example.com")
    debt_a = await _create_debt(client, headers_a)
    r = await client.post(
        f"/api/v1/debts/{debt_a['id']}/payments",
        json={"amount": MIN_PAYMENT, "payment_date": today.isoformat()},
        headers=headers_a,
    )
    assert r.status_code == 201, r.text
    pay2 = r.json()
    events_a = await _current_month_events(client, headers_a)
    event_a = next(e for e in events_a if e.get("obligation_id"))
    assert event_a["paid_by"] is None

    # --- Flujo 3 (pago desde evento), hogar B
    headers_b = await _register(client, "char_diff_b@example.com")
    debt_b = await _create_debt(client, headers_b)
    events_b = await _current_month_events(client, headers_b)
    event_b = next(e for e in events_b if e.get("obligation_id"))
    r = await client.post(f"/api/v1/events/{event_b['id']}/pay", headers=headers_b)
    assert r.status_code == 200, r.text
    event_b_paid = r.json()

    r = await client.get(f"/api/v1/debts/{debt_b['id']}/payments", headers=headers_b)
    pay3 = r.json()[0]

    # idénticos: interés, principal y saldo final
    assert pay3["interest"] == pay2["interest"] == INTEREST
    assert pay3["principal"] == pay2["principal"] == PRINCIPAL
    r = await client.get(f"/api/v1/debts/{debt_b['id']}", headers=headers_b)
    r2 = await client.get(f"/api/v1/debts/{debt_a['id']}", headers=headers_a)
    assert r.json()["current_balance"] == r2.json()["current_balance"] == NEW_BALANCE

    # DIFERENCIA 1: fecha del pago
    assert pay2["payment_date"] == today.isoformat()
    assert pay3["payment_date"] == event_b["due_date"]

    # DIFERENCIA 2: quién aparece como pagador en el evento
    assert event_a["paid_by"] is None
    assert event_b_paid["paid_by"] is not None

    # DIFERENCIA 3: monto registrado como pagado
    assert event_a["paid_amount"] == MIN_PAYMENT          # monto real pagado
    assert event_b_paid["paid_amount"] == event_b["amount"]  # monto del evento

    # Común: ninguno de los dos caminos crea transacción
    assert await _get_transactions(client, headers_a) == []
    assert await _get_transactions(client, headers_b) == []


# ---------------------------------------------------------------- Flujo 4

@pytest.mark.anyio
async def test_flujo4_pago_recurrente_crea_transaccion_sin_avanzar_next_due(client):
    """FLUJO 4 (congelado): pago recurrente cobrado desde el calendario."""
    headers = await _register(client, "char_flow4@example.com")
    account = await _create_account(client, headers, "1000000")

    r = await client.post("/api/v1/recurring-payments", json={
        "name": "Streaming",
        "amount": RECURRING_AMOUNT,
        "type": "expense",
        "frequency": "monthly",
        "day_of_month": 15,
    }, headers=headers)
    assert r.status_code == 201, r.text
    recurring = r.json()
    assert recurring["next_due_date"] is not None
    before_next_due = recurring["next_due_date"]

    # el sistema creó la obligación + eventos
    r = await client.get(
        f"/api/v1/recurring-payments/{recurring['id']}/pending-event",
        headers=headers,
    )
    assert r.status_code == 200, r.text
    event = r.json()
    assert event["status"] == "pending"
    assert event["is_recurrent"] is True
    assert event["obligation_id"] is not None

    # cobrar desde el calendario
    r = await client.post(f"/api/v1/events/{event['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "paid"

    # 1) transacción creada
    txs = await _get_transactions(client, headers)
    assert len(txs) == 1
    assert txs[0]["type"] == "expense"
    assert txs[0]["amount"] == RECURRING_AMOUNT
    assert "recurring_payment_id" not in txs[0], (
        "CONGELADO: TransactionResponse no expone recurring_payment_id, "
        "el vínculo transacción↔recurrente es invisible para el cliente"
    )
    assert txs[0]["date"] == event["due_date"], (
        "CONGELADO: la transacción se fecha con la fecha de vencimiento, no con hoy"
    )

    # 2) el evento cobrado queda pagado y el siguiente pendiente queda disponible
    r = await client.get(
        f"/api/v1/recurring-payments/{recurring['id']}/pending-event",
        headers=headers,
    )
    assert r.status_code == 200, (
        "CONGELADO: tras cobrar, pending-event devuelve el SIGUIENTE evento "
        "del mismo pago recurrente (la serie ya tiene 12 eventos generados)"
    )
    next_event = r.json()
    assert next_event["id"] != event["id"]
    assert next_event["status"] == "pending"
    assert next_event["due_date"] > event["due_date"]

    # 3) DEFECTO CONGELADO: next_due_date NO avanza
    r = await client.get(f"/api/v1/recurring-payments/{recurring['id']}", headers=headers)
    after_next_due = r.json()["next_due_date"]
    assert after_next_due == before_next_due, (
        "CONGELADO: crear y pagar calculan next_due_date con la MISMA fórmula "
        "«mes siguiente desde hoy», así que el pago nunca lo mueve"
    )

    # 4) la cuenta se debita
    r = await client.get(f"/api/v1/accounts/{account['id']}", headers=headers)
    assert r.json()["balance"] == "955000.00"

    # DEFECTO CONGELADO (D-5): el cobro desde calendario NO escribe balance_history
    r = await client.get(f"/api/v1/balance-history/{account['id']}", headers=headers)
    assert r.status_code == 200
    assert r.json()["history"] == [], (
        "CONGELADO: event_service ajusta el saldo SIN registrar balance_history "
        "(hallazgo D-5 de 6.4A)"
    )


@pytest.mark.anyio
async def test_flujo4_camino_b_recurring_pay_no_marca_evento_pagado(client):
    """DEFECTO CONGELADO (D-4): existen dos ejecutores de pago recurrente.

    POST /recurring-payments/{id}/pay crea transacción, debita la cuenta y
    recalcula next_due_date, pero NO marca el evento del calendario como
    pagado → los dos caminos divergen.
    """
    headers = await _register(client, "char_flow4b@example.com")
    account = await _create_account(client, headers, "1000000")

    r = await client.post("/api/v1/recurring-payments", json={
        "name": "Internet",
        "amount": RECURRING_AMOUNT,
        "type": "expense",
        "frequency": "monthly",
        "day_of_month": 10,
    }, headers=headers)
    assert r.status_code == 201, r.text
    recurring = r.json()

    r = await client.get(
        f"/api/v1/recurring-payments/{recurring['id']}/pending-event",
        headers=headers,
    )
    assert r.status_code == 200, r.text
    event = r.json()
    assert event["status"] == "pending"

    r = await client.post(
        f"/api/v1/recurring-payments/{recurring['id']}/pay",
        headers=headers,
    )
    assert r.status_code == 200, r.text
    after = r.json()
    assert after["next_due_date"] == recurring["next_due_date"], (
        "CONGELADO: el Camino B recalcula next_due_date como «mes siguiente "
        "desde hoy», idéntico al valor creado → el pago NO lo mueve"
    )

    txs = await _get_transactions(client, headers)
    assert len(txs) == 1
    assert "recurring_payment_id" not in txs[0]
    assert txs[0]["description"] == "Internet"
    assert txs[0]["date"] == date.today().isoformat(), (
        "DIFERENCIA vs Camino A: el Camino B fecha la transacción con HOY, "
        "el Camino A con la fecha de vencimiento del evento"
    )

    # el evento sigue pendiente → el calendario no se enteró
    r = await client.get(
        f"/api/v1/recurring-payments/{recurring['id']}/pending-event",
        headers=headers,
    )
    assert r.status_code == 200, (
        "CONGELADO: el Camino B deja el evento pendiente mientras cobra "
        "(hallazgo D-4 de 6.4A) → se puede cobrar dos veces"
    )
    assert r.json()["id"] == event["id"], "sigue siendo el MISMO evento pendiente"

    # la cuenta sí se debita
    r = await client.get(f"/api/v1/accounts/{account['id']}", headers=headers)
    assert r.json()["balance"] == "955000.00"

    # también deja el balance_history vacío (misma deuda técnica que el Camino A)
    r = await client.get(f"/api/v1/balance-history/{account['id']}", headers=headers)
    assert r.json()["history"] == []
