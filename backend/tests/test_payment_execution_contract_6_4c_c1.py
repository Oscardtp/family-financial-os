"""FASE 6.4C-C1 — Tests de contrato / reproducción de ejecución monetaria.

ESTOS TESTS NO VALIDAN EL COMPORTAMIENTO ACTUAL.
Definen el comportamiento objetivo de la FASE 6.4C-C2 y deben FALLAR contra el
código de hoy (rojo) para dirigir la implementación.

Hallazgos cubiertos (auditoría 6.4A + C0):
  G-1  pago de deuda crea exactamente una Transaction y enlaza DebtPayment
  D-4  un ciclo de pago = una sola Transaction (rutas recurrente/evento)
  D-5  toda Transaction pasa por la autoridad monetaria (balance_history + household_id)
  G-6  mark_month_paid no puede descontar dinero inexistente ni dos veces
  G-7  unpay debe dejar el dinero consistente (mecanismo pendiente de decisión)
  HH   household_id obligatorio + aislamiento entre hogares
  MATH matemática de deuda congelada (interés / principal / saldo)

RESTRICCIONES RESPETADAS:
  * No se modifica producción, modelos, migraciones ni frontend.
  * No se modifica `tests/test_characterization_6_4b.py` (sigue congelando G-1,
    D-4 y D-5; C2 lo actualizará con ADR después de corregir).
  * No se modifican los 3 tests preexistentes fallidos de `tests/test_calendar.py`.
  * No se toca `NextDueDateService` (FASE 6.4C-B).
  * No se crean entidades ni columnas nuevas.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import select

from app.infrastructure.models.models import (
    AccountBalanceHistoryModel,
    DebtPaymentModel,
    TransactionModel,
)


# ---------------------------------------------------------------- constantes
# Deterministas (mismas de test_characterization_6_4b.py):
# saldo 1.000.000 · 2% EM → interés 20.000,00 · cuota 100.000 → principal 80.000,00
BALANCE = "1000000.00"
INTEREST = "20000.00"
PRINCIPAL = "80000.00"
NEW_BALANCE = "920000.00"
MIN_PAYMENT = "100000.00"
RECURRING_AMOUNT = "45000.00"
ACCOUNT_AFTER_RECURRING = "955000.00"


# ---------------------------------------------------------------- helpers API

async def _register(client, email: str) -> dict:
    r = await client.post("/api/v1/auth/register", json={
        "email": email,
        "name": "Contrato C1",
        "password": "password123",
    })
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _create_account(client, headers: dict, balance: str = "1000000") -> dict:
    r = await client.post("/api/v1/accounts", json={
        "name": "Cuenta contrato C1",
        "type": "bank",
        "balance": balance,
    }, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


async def _create_debt(client, headers: dict, **overrides) -> dict:
    payload = {
        "name": "Deuda contrato C1",
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
    """Ventana segura: mes en curso + 14 meses (misma fórmula que caracterización)."""
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


async def _debt_event(client, headers: dict) -> dict:
    """Primer evento generado por la obligación SYSTEM de la deuda."""
    start, end = _event_window()
    events = await _get_events(client, headers, start, end)
    debt_events = [e for e in events if e.get("obligation_id")]
    assert debt_events, "la creación de la deuda debe haber generado eventos"
    return debt_events[0]


async def _create_recurring(
    client,
    headers: dict,
    *,
    name: str,
    account_id: str,
    day_of_month: int,
    next_due_date: date,
    amount: str = RECURRING_AMOUNT,
) -> dict:
    r = await client.post("/api/v1/recurring-payments", json={
        "name": name,
        "amount": amount,
        "type": "expense",
        "frequency": "monthly",
        "day_of_month": day_of_month,
        "account_id": account_id,
        "next_due_date": next_due_date.isoformat(),
    }, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


async def _pending_event(client, headers: dict, payment_id: str) -> dict:
    r = await client.get(
        f"/api/v1/recurring-payments/{payment_id}/pending-event", headers=headers
    )
    assert r.status_code == 200, r.text
    return r.json()


async def _account_balance(client, headers: dict, account_id: str) -> Decimal:
    r = await client.get(f"/api/v1/accounts/{account_id}", headers=headers)
    assert r.status_code == 200, r.text
    return Decimal(str(r.json()["balance"]))


async def _debt_balance(client, headers: dict, debt_id: str) -> Decimal:
    r = await client.get(f"/api/v1/debts/{debt_id}", headers=headers)
    assert r.status_code == 200, r.text
    return Decimal(str(r.json()["current_balance"]))


async def _pay_debt_endpoint(client, headers: dict, debt_id: str, amount: str = MIN_PAYMENT):
    r = await client.post(
        f"/api/v1/debts/{debt_id}/payments",
        json={"amount": amount, "payment_date": date.today().isoformat()},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _pay_event(client, headers: dict, event_id: str) -> dict:
    r = await client.post(f"/api/v1/events/{event_id}/pay", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


async def _balance_history(client, headers: dict, account_id: str) -> list[dict]:
    r = await client.get(f"/api/v1/balance-history/{account_id}", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()["history"]


# ---------------------------------------------------------------- helpers DB
# TransactionResponse y DebtPaymentResponse NO exponen household_id ni
# transaction_id: para esos contratos hay que leer el modelo. Cada lectura se
# cierra con rollback para no retener bloqueo de lectura sobre SQLite.

async def _db_transactions(session) -> list[dict]:
    rows = (await session.execute(select(TransactionModel))).scalars().all()
    data = [{
        "id": str(m.id),
        "household_id": str(m.household_id) if m.household_id else None,
        "account_id": str(m.account_id),
        "type": m.type,
        "amount": Decimal(str(m.amount)),
        "date": m.date,
        "description": m.description,
        "recurring_payment_id": str(m.recurring_payment_id) if m.recurring_payment_id else None,
    } for m in rows]
    await session.rollback()
    return data


async def _db_debt_payments(session, debt_id: str | None = None) -> list[dict]:
    stmt = select(DebtPaymentModel)
    if debt_id:
        stmt = stmt.where(DebtPaymentModel.debt_id == str(debt_id))
    rows = (await session.execute(stmt)).scalars().all()
    data = [{
        "id": str(m.id),
        "debt_id": str(m.debt_id),
        "amount": Decimal(str(m.amount)),
        "principal": Decimal(str(m.principal)) if m.principal is not None else None,
        "interest": Decimal(str(m.interest)) if m.interest is not None else None,
        "payment_date": m.payment_date,
        "is_reversed": bool(m.is_reversed),
        "transaction_id": str(m.transaction_id) if m.transaction_id else None,
        "household_id": str(m.household_id) if m.household_id else None,
    } for m in rows]
    await session.rollback()
    return data


async def _db_balance_history(session, account_id: str) -> list[dict]:
    rows = (await session.execute(
        select(AccountBalanceHistoryModel).where(
            AccountBalanceHistoryModel.account_id == str(account_id)
        )
    )).scalars().all()
    data = [{
        "transaction_id": str(m.transaction_id) if m.transaction_id else None,
        "balance_before": Decimal(str(m.balance_before)),
        "balance_after": Decimal(str(m.balance_after)),
        "change_amount": Decimal(str(m.change_amount)),
        "change_type": m.change_type,
    } for m in rows]
    await session.rollback()
    return data


# ================================================================================
# 1. G-1 — Pago de deuda debe crear Transaction
# ================================================================================

@pytest.mark.anyio
async def test_g1a_pago_de_deuda_endpoint_crea_exactamente_una_transaction(client, session):
    """CONTRATO G-1: `POST /debts/{id}/payments` registra dinero real ⇒ 1 Transaction."""
    headers = await _register(client, "c1_g1a@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)

    await _pay_debt_endpoint(client, headers, debt["id"])

    txs = await _db_transactions(session)
    assert len(txs) == 1, (
        "CONTRATO G-1: pagar la deuda debe crear exactamente una Transaction; "
        f"hoy hay {len(txs)} — el dinero pagado no queda registrado (hallazgo G-1 de 6.4A)."
    )
    assert txs[0]["type"] == "expense"
    assert txs[0]["amount"] == Decimal(MIN_PAYMENT)
    assert txs[0]["date"] == date.today()


@pytest.mark.anyio
async def test_g1b_pago_de_deuda_desde_evento_crea_exactamente_una_transaction(client, session):
    """CONTRATO G-1: `POST /events/{id}/pay` sobre evento de deuda ⇒ 1 Transaction."""
    headers = await _register(client, "c1_g1b@example.com")
    await _create_account(client, headers, "1000000")
    await _create_debt(client, headers)
    event = await _debt_event(client, headers)

    await _pay_event(client, headers, event["id"])

    txs = await _db_transactions(session)
    assert len(txs) == 1, (
        "CONTRATO G-1: pagar el evento de la deuda debe crear exactamente una Transaction; "
        f"hoy hay {len(txs)} — `_create_transaction_for_recurring_event` resuelve un "
        "RecurringPayment que no existe para deudas y sale sin crear nada (G-1)."
    )
    assert txs[0]["amount"] == Decimal(MIN_PAYMENT)
    assert txs[0]["type"] == "expense"


@pytest.mark.anyio
async def test_g1c_pago_endpoint_descuenta_el_saldo_de_la_deuda_una_sola_vez(client):
    """CONTRATO G-1: el `current_balance` baja exactamente una vez (sin doble descuento)."""
    headers = await _register(client, "c1_g1c@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)

    await _pay_debt_endpoint(client, headers, debt["id"])

    assert await _debt_balance(client, headers, debt["id"]) == Decimal(NEW_BALANCE), (
        "CONTRATO G-1: un solo pago de 100.000 sobre 1.000.000 al 2% EM debe dejar "
        f"{NEW_BALANCE} exactos (interés 20.000 + principal 80.000)."
    )


@pytest.mark.anyio
async def test_g1d_pago_desde_evento_descuenta_el_saldo_de_la_deuda_una_sola_vez(client):
    """CONTRATO G-1: la ruta del calendario aplica exactamente la misma matemática una vez."""
    headers = await _register(client, "c1_g1d@example.com")
    await _create_account(client, headers, "1000000")
    await _create_debt(client, headers)
    event = await _debt_event(client, headers)

    await _pay_event(client, headers, event["id"])

    debt_id = (await client.get(
        "/api/v1/debts", headers=headers
    )).json()[0]["id"]
    assert await _debt_balance(client, headers, debt_id) == Decimal(NEW_BALANCE), (
        "CONTRATO G-1: pagar desde el evento debe descontar principal una sola vez."
    )


@pytest.mark.anyio
async def test_g1e_transaction_del_pago_de_deuda_lleva_household_id(client, session):
    """CONTRATO G-1/HH: toda Transaction de pago de deuda lleva `household_id`."""
    headers = await _register(client, "c1_g1e@example.com")
    account = await _create_account(client, headers, "1000000")
    household_id = account["household_id"]
    debt = await _create_debt(client, headers)

    await _pay_debt_endpoint(client, headers, debt["id"])

    txs = await _db_transactions(session)
    assert txs, "CONTRATO G-1: debe existir la Transaction del pago de la deuda."
    assert txs[0]["household_id"] == household_id, (
        "CONTRATO HH: la Transaction del pago de deuda debe portar household_id; "
        f"esperado {household_id}, obtenido {txs[0]['household_id']}."
    )


# ================================================================================
# 2. D-4 — Pago recurrente debe converger con el evento (un ciclo = una Transaction)
# ================================================================================

@pytest.mark.anyio
async def test_d4a_ruta_recurrente_y_ruta_evento_no_duplican_transaction(client, session):
    """CONTRATO D-4: mismo ciclo, dos rutas ⇒ UNA sola Transaction."""
    headers = await _register(client, "c1_d4a@example.com")
    account = await _create_account(client, headers, "1000000")
    today = date.today()
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D4A", account_id=account["id"],
        day_of_month=today.day, next_due_date=today,
    )
    event = await _pending_event(client, headers, rp["id"])

    # Camino B — pago directo del recurrente
    r = await client.post(f"/api/v1/recurring-payments/{rp['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text

    # Camino A — el usuario cobra el mismo ciclo desde el calendario
    await _pay_event(client, headers, event["id"])

    txs = await _db_transactions(session)
    assert len(txs) == 1, (
        "CONTRATO D-4: un mismo ciclo sólo puede producir una Transaction; se crearon "
        f"{len(txs)} — `RecurringPaymentService._execute_payment` no cierra el ciclo y "
        "el evento sigue cobrable (hallazgo D-4 de 6.4A)."
    )
    assert {t["recurring_payment_id"] for t in txs} == {rp["id"]}


@pytest.mark.anyio
async def test_d4b_un_ciclo_debita_la_cuenta_solo_una_vez(client):
    """CONTRATO D-4: el saldo de la cuenta se mueve una sola vez por ciclo."""
    headers = await _register(client, "c1_d4b@example.com")
    account = await _create_account(client, headers, "1000000")
    today = date.today()
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D4B", account_id=account["id"],
        day_of_month=today.day, next_due_date=today,
    )
    event = await _pending_event(client, headers, rp["id"])

    await client.post(f"/api/v1/recurring-payments/{rp['id']}/pay", headers=headers)
    await _pay_event(client, headers, event["id"])

    assert await _account_balance(client, headers, account["id"]) == Decimal(
        ACCOUNT_AFTER_RECURRING
    ), (
        "CONTRATO D-4: la cuenta debe debitar 45.000 UNA vez por ciclo "
        f"(esperado {ACCOUNT_AFTER_RECURRING}); el doble cobro la deja en "
        f"{await _account_balance(client, headers, account['id'])}."
    )


@pytest.mark.anyio
async def test_d4c_tras_pagar_por_ruta_recurrente_el_evento_del_ciclo_queda_cerrado(client):
    """CONTRATO D-4: pagar por la ruta recurrente cierra el evento del calendario."""
    headers = await _register(client, "c1_d4c@example.com")
    account = await _create_account(client, headers, "1000000")
    today = date.today()
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D4C", account_id=account["id"],
        day_of_month=today.day, next_due_date=today,
    )
    event = await _pending_event(client, headers, rp["id"])

    r = await client.post(f"/api/v1/recurring-payments/{rp['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text

    r = await client.get(
        f"/api/v1/recurring-payments/{rp['id']}/pending-event", headers=headers
    )
    assert r.status_code == 200, "la serie tiene 12 eventos generados; debe quedar otro pendiente"
    next_event = r.json()
    assert next_event["id"] != event["id"], (
        "CONTRATO D-4: tras pagar por la ruta recurrente, el evento del ciclo debe quedar "
        f"pagado; `pending-event` sigue devolviendo el MISMO evento {event['id']} "
        "⇒ el calendario no se enteró y el ciclo es re-cobrable (D-4)."
    )


@pytest.mark.anyio
async def test_d4d_process_due_y_evento_no_duplican_transaction(client, session):
    """CONTRATO D-4: `process_due` + cobro manual del mismo ciclo ⇒ UNA Transaction."""
    headers = await _register(client, "c1_d4d@example.com")
    account = await _create_account(client, headers, "1000000")
    today = date.today()
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D4D", account_id=account["id"],
        day_of_month=today.day, next_due_date=today,
    )
    event = await _pending_event(client, headers, rp["id"])

    r = await client.post("/api/v1/recurring-payments/process-due", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["processed"] == 1, "el lote debe haber procesado el pago vencido hoy"

    # El evento del ciclo sigue pendiente y el usuario lo cobra desde el calendario
    await _pay_event(client, headers, event["id"])

    txs = await _db_transactions(session)
    assert len(txs) == 1, (
        "CONTRATO D-4: `process-due` y el cobro manual del mismo ciclo no pueden "
        f"producir dos Transactions; hay {len(txs)}."
    )


@pytest.mark.anyio
async def test_d4e_pago_desde_evento_y_luego_directo_no_duplican_transaction(client, session):
    """CONTRATO D-4: primer pago desde el evento, después ruta directa ⇒ UNA Transaction."""
    headers = await _register(client, "c1_d4e@example.com")
    account = await _create_account(client, headers, "1000000")
    today = date.today()
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D4E", account_id=account["id"],
        day_of_month=today.day, next_due_date=today,
    )
    event = await _pending_event(client, headers, rp["id"])

    # Camino A — el usuario cobra el ciclo desde el calendario
    await _pay_event(client, headers, event["id"])

    # Camino B — el usuario vuelve a pagar por la ruta directa el mismo día
    r = await client.post(f"/api/v1/recurring-payments/{rp['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text

    txs = await _db_transactions(session)
    assert len(txs) == 1, (
        "CONTRATO D-4: tras cobrar desde el evento, la ruta directa del mismo día "
        f"debe tratarse como «ya pagado» y no crear otra Transaction; hay {len(txs)}."
    )
    assert await _account_balance(client, headers, account["id"]) == Decimal(
        ACCOUNT_AFTER_RECURRING
    ), (
        "CONTRATO D-4: la cuenta sólo puede debitar 45.000 UNA vez por ciclo "
        "sin importar el orden de las rutas."
    )


# ================================================================================
# 3. D-5 — Toda Transaction debe pasar por la autoridad monetaria
# ================================================================================

@pytest.mark.anyio
async def test_d5a_cobro_desde_evento_registra_balance_history(client):
    """CONTRATO D-5: el cobro desde calendario debe escribir `account_balance_history`."""
    headers = await _register(client, "c1_d5a@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D5A", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    event = await _pending_event(client, headers, rp["id"])

    await _pay_event(client, headers, event["id"])

    history = await _balance_history(client, headers, account["id"])
    assert len(history) >= 1, (
        "CONTRATO D-5: mutar `Account.balance` debe registrar `account_balance_history`; "
        "hoy `event_service` debita el saldo sin historial (hallazgo D-5 de 6.4A)."
    )


@pytest.mark.anyio
async def test_d5b_cobro_por_ruta_recurrente_registra_balance_history(client):
    """CONTRATO D-5: la ruta recurrente también debe pasar por la autoridad monetaria."""
    headers = await _register(client, "c1_d5b@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D5B", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    await _pending_event(client, headers, rp["id"])

    r = await client.post(f"/api/v1/recurring-payments/{rp['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text

    history = await _balance_history(client, headers, account["id"])
    assert len(history) >= 1, (
        "CONTRATO D-5: `RecurringPaymentService._execute_payment` muta el saldo sin "
        "escribir `account_balance_history` (hallazgo D-5 de 6.4A)."
    )


@pytest.mark.anyio
async def test_d5c_balance_history_refleja_el_movimiento_del_cobro(client, session):
    """CONTRATO D-5: before/after/change deben ser coherentes con el saldo real."""
    headers = await _register(client, "c1_d5c@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D5C", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    event = await _pending_event(client, headers, rp["id"])

    await _pay_event(client, headers, event["id"])

    history = await _db_balance_history(session, account["id"])
    assert len(history) >= 1, (
        "CONTRATO D-5: el cobro debe producir al menos un registro de balance_history."
    )
    record = history[0]
    assert record["change_type"] == "expense"
    assert record["change_amount"] == Decimal("-" + RECURRING_AMOUNT)
    assert record["balance_before"] - Decimal(RECURRING_AMOUNT) == record["balance_after"]
    assert record["transaction_id"] is not None, (
        "CONTRATO D-5: el registro de historial debe apuntar a la Transaction que lo causó."
    )
    assert record["balance_after"] == await _account_balance(
        client, headers, account["id"]
    )


@pytest.mark.anyio
async def test_d5c2_process_due_registra_balance_history(client):
    """CONTRATO D-5 (D5-C): `POST /recurring-payments/process-due` delega en la autoridad.

    Antes de C2a-2, `process-due` compartía con la ruta directa un
    `_execute_payment` que mutaba `Account.balance` sin registrar
    `account_balance_history` ⇒ este contrato estaba en rojo, igual que D5-B.
    """
    headers = await _register(client, "c1_d5c2@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo D5C2", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    await _pending_event(client, headers, rp["id"])

    r = await client.post("/api/v1/recurring-payments/process-due", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["processed"] == 1, "el lote debe haber procesado el pago vencido hoy"

    history = await _balance_history(client, headers, account["id"])
    assert len(history) >= 1, (
        "CONTRATO D-5: `process-due` debe mutar el saldo a través de "
        "`TransactionService`, que escribe `account_balance_history`."
    )
    assert history[0]["change_type"] == "expense"
    assert Decimal(str(history[0]["change_amount"])) == Decimal("-" + RECURRING_AMOUNT)
    assert await _account_balance(client, headers, account["id"]) == Decimal(
        ACCOUNT_AFTER_RECURRING
    )


@pytest.mark.anyio
async def test_d5d_un_solo_lugar_del_codigo_muta_el_saldo_de_cuenta():
    """CONTRATO D-5: `TransactionService` es el ÚNICO mutador de `Account.balance`.

    No puede existir una segunda implementación de `_check_balance`,
    `_adjust_balances`, `update_balance` ni `deduct_balance` fuera de la autoridad
    monetaria. Es una restricción arquitectónica (A6), no un detalle interno:
    se verifica sobre la estructura del código de la capa Application/Infrastructure.
    """
    backend_root = Path(__file__).resolve().parents[1]
    app_root = backend_root / "app"

    allowed_files = {"transaction_service.py", "account_repository.py"}
    balance_callers: list[str] = []
    duplicate_helpers: list[str] = []

    for path in sorted(app_root.rglob("*.py")):
        if "interfaces" in path.parts or path.name in allowed_files:
            continue
        source = path.read_text(encoding="utf8")
        if "update_balance(" in source or "deduct_balance(" in source:
            balance_callers.append(str(path.relative_to(backend_root)))
        if "def _check_balance" in source or "def _adjust_balances" in source:
            duplicate_helpers.append(str(path.relative_to(backend_root)))

    assert not duplicate_helpers, (
        "CONTRATO D-5: `_check_balance`/`_adjust_balances` sólo pueden vivir en "
        f"transaction_service.py; duplicados en: {duplicate_helpers}"
    )
    assert not balance_callers, (
        "CONTRATO D-5: nadie fuera de la autoridad monetaria puede llamar "
        f"`update_balance`/`deduct_balance`; encontrados en: {balance_callers} "
        "— hoy existen mutadores alternativos de saldo (D-4/D-5 de 6.4A)."
    )


# ================================================================================
# 4. G-6 — mark_month_paid no puede descontar dinero inexistente
# ================================================================================

@pytest.mark.anyio
async def test_g6a_mark_month_paid_no_descuenta_una_segunda_vez_el_mismo_periodo(client):
    """CONTRATO G-6: pago real + mark-paid del MISMO período ⇒ un solo descuento."""
    headers = await _register(client, "c1_g6a@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)

    await _pay_debt_endpoint(client, headers, debt["id"])
    assert await _debt_balance(client, headers, debt["id"]) == Decimal(NEW_BALANCE)

    today = date.today()
    r = await client.post(
        f"/api/v1/debts/{debt['id']}/mark-paid",
        json={"year": today.year, "month": today.month},
        headers=headers,
    )
    assert r.status_code == 201, r.text

    assert await _debt_balance(client, headers, debt["id"]) == Decimal(NEW_BALANCE), (
        "CONTRATO G-6: `mark_month_paid` no puede volver a descontar el mismo período "
        "cuando ya existe un pago real — el saldo se redujo dos veces por un solo mes."
    )


@pytest.mark.anyio
async def test_g6b_mark_month_paid_no_modifica_el_saldo_de_cuenta(client):
    """CONTRATO G-6: sin movimiento real de dinero, la cuenta no se toca."""
    headers = await _register(client, "c1_g6b@example.com")
    account = await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)
    before = await _account_balance(client, headers, account["id"])

    today = date.today()
    r = await client.post(
        f"/api/v1/debts/{debt['id']}/mark-paid",
        json={"year": today.year, "month": today.month},
        headers=headers,
    )
    assert r.status_code == 201, r.text

    assert await _account_balance(client, headers, account["id"]) == before, (
        "CONTRATO G-6: marcar un mes como pagado no mueve dinero de la cuenta "
        "(no existe transacción real que lo justifique)."
    )


@pytest.mark.anyio
async def test_g6c_mark_month_paid_duplicado_en_el_mismo_periodo_es_rechazado(client):
    """CONTRATO G-6: no se puede marcar dos veces el mismo período."""
    headers = await _register(client, "c1_g6c@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)
    today = date.today()
    payload = {"year": today.year, "month": today.month}

    first = await client.post(f"/api/v1/debts/{debt['id']}/mark-paid", json=payload, headers=headers)
    assert first.status_code == 201, first.text
    second = await client.post(f"/api/v1/debts/{debt['id']}/mark-paid", json=payload, headers=headers)
    assert second.status_code == 400, (
        "CONTRATO G-6: el segundo mark-paid del mismo período debe rechazarse (400)."
    )


@pytest.mark.anyio
async def test_g6d_mark_month_paid_sin_pago_real_no_crea_dinero(client, session):
    """CONTRATO G-6 + CONFLICTO DE SEMÁNTICA DOCUMENTADO (sin resolver aquí).

    Conflicto: `POST /debts/{id}/mark-paid` describe «marcar un mes histórico como
    pagado SIN registrar un pago real», pero hoy descuenta `current_balance`
    (`debt_service.py:161-163`). En el modelo aprobado sólo una Transaction es
    dinero ejecutado, así que DESCUENTAR SIN DINERO choca con la cadena
    `Debt → … → Transaction → Saldo`.

    Decisión arquitectónica pendiente (NO se inventa solución en C1):
      (a) mark_month_paid NO descuenta saldo (sólo cambia el estado del mes), o
      (b) mark_month_paid sí descuenta y exige una Transaction real asociada.

    Este test sólo fija lo que es inequívoco hoy: no crea Transaction ni toca cuentas.
    """
    headers = await _register(client, "c1_g6d@example.com")
    account = await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)

    today = date.today()
    r = await client.post(
        f"/api/v1/debts/{debt['id']}/mark-paid",
        json={"year": today.year, "month": today.month},
        headers=headers,
    )
    assert r.status_code == 201, r.text

    txs = await _db_transactions(session)
    assert txs == [], (
        "CONTRATO G-6: marcar un mes sin pago real no debe crear dinero ejecutado; "
        "si C2 elige la opción (b), este test deberá actualizarse con ADR."
    )
    assert await _account_balance(client, headers, account["id"]) == Decimal("1000000.00")


# ================================================================================
# 5. DebtPayment.transaction_id → Transaction (FK ya existente, nunca poblada)
# ================================================================================

@pytest.mark.anyio
async def test_debtpayment_transaction_id_enlazado_en_pago_endpoint(client, session):
    """CONTRATO: tras un pago real, `DebtPayment.transaction_id` apunta a la Transaction."""
    headers = await _register(client, "c1_dpid_a@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)

    payment = await _pay_debt_endpoint(client, headers, debt["id"])

    payments = await _db_debt_payments(session, debt["id"])
    assert len(payments) == 1
    assert payments[0]["id"] == payment["id"]
    assert payments[0]["transaction_id"] is not None, (
        "CONTRATO: `debt_payments.transaction_id` (FK RESTRICT, models.py:132) está "
        "declarada pero nunca se escribe ⇒ el pago no queda ligado al dinero."
    )

    txs = await _db_transactions(session)
    assert txs and payments[0]["transaction_id"] == txs[0]["id"], (
        "CONTRATO: `DebtPayment.transaction_id` debe apuntar a la Transaction de ese pago."
    )


@pytest.mark.anyio
async def test_debtpayment_transaction_id_enlazado_en_pago_desde_evento(client, session):
    """CONTRATO: la ruta del calendario también enlaza DebtPayment ↔ Transaction."""
    headers = await _register(client, "c1_dpid_b@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)
    event = await _debt_event(client, headers)

    await _pay_event(client, headers, event["id"])

    payments = await _db_debt_payments(session, debt["id"])
    assert len(payments) == 1, "CONTRATO: el evento de deuda debe registrar un DebtPayment."
    assert payments[0]["transaction_id"] is not None, (
        "CONTRATO: `DebtPayment.transaction_id` debe quedar poblada también cuando "
        "el pago nace en el calendario."
    )

    txs = await _db_transactions(session)
    assert txs and payments[0]["transaction_id"] == txs[0]["id"]


# ================================================================================
# 6. household_id obligatorio + aislamiento
# ================================================================================

@pytest.mark.anyio
async def test_hh_transaction_del_cobro_recurrente_lleva_household_id(client, session):
    """CONTRATO HH: la Transaction de `POST /recurring-payments/{id}/pay` porta household_id."""
    headers = await _register(client, "c1_hh_a@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo HH", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    await _pending_event(client, headers, rp["id"])

    r = await client.post(f"/api/v1/recurring-payments/{rp['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text

    txs = await _db_transactions(session)
    assert txs, "CONTRATO: la ruta recurrente debe crear una Transaction."
    assert txs[0]["household_id"] == account["household_id"], (
        "CONTRATO HH: `_execute_payment` crea la Transaction SIN household_id "
        f"(obtenido {txs[0]['household_id']}) ⇒ rompe el aislamiento por hogar."
    )


@pytest.mark.anyio
async def test_hh_transaction_del_cobro_desde_evento_lleva_household_id(client, session):
    """CONTRATO HH: la Transaction nacida en el calendario porta household_id."""
    headers = await _register(client, "c1_hh_b@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo HH B", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    event = await _pending_event(client, headers, rp["id"])

    await _pay_event(client, headers, event["id"])

    txs = await _db_transactions(session)
    assert txs, "CONTRATO: el cobro desde evento debe crear una Transaction."
    assert txs[0]["household_id"] == account["household_id"]


@pytest.mark.anyio
async def test_hh_historial_del_recurrente_incluye_el_pago_de_la_ruta_b(client):
    """CONTRATO HH: `GET /recurring-payments/{id}/payments` ve cualquier ruta de cobro.

    `get_by_recurring` filtra por `TransactionModel.household_id`; la ruta recurrente
    escribe NULL ⇒ su propio pago desaparece del historial.
    """
    headers = await _register(client, "c1_hh_c@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo HH C", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    await _pending_event(client, headers, rp["id"])

    r = await client.post(f"/api/v1/recurring-payments/{rp['id']}/pay", headers=headers)
    assert r.status_code == 200, r.text

    history = await client.get(
        f"/api/v1/recurring-payments/{rp['id']}/payments", headers=headers
    )
    assert history.status_code == 200, history.text
    rows = history.json()
    assert len(rows) == 1, (
        "CONTRATO HH: el pago hecho por la propia ruta recurrente debe aparecer en su "
        f"historial; hoy devuelve {len(rows)} fila(s) porque la Transaction no tiene "
        "household_id."
    )
    assert Decimal(str(rows[0]["amount"])) == Decimal(RECURRING_AMOUNT)


@pytest.mark.anyio
async def test_hh_aislamiento_de_transacciones_entre_households(client, session):
    """CONTRATO HH: una Transaction del hogar A nunca aparece en el hogar B."""
    headers_a = await _register(client, "c1_hh_iso_a@example.com")
    account_a = await _create_account(client, headers_a, "1000000")
    rp = await _create_recurring(
        client, headers_a,
        name="Ciclo Aislamiento", account_id=account_a["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    event = await _pending_event(client, headers_a, rp["id"])
    await _pay_event(client, headers_a, event["id"])

    headers_b = await _register(client, "c1_hh_iso_b@example.com")
    account_b = await _create_account(client, headers_b, "1000000")

    visible_b = await client.get("/api/v1/transactions", headers=headers_b)
    assert visible_b.status_code == 200
    assert visible_b.json() == [], (
        "CONTRATO HH: el hogar B no debe ver transacciones del hogar A."
    )

    txs = await _db_transactions(session)
    assert txs, "el hogar A debe tener su Transaction"
    assert all(t["household_id"] != account_b["household_id"] for t in txs)
    assert all(t["household_id"] == account_a["household_id"] for t in txs)


# ================================================================================
# 7. Matemática de deuda (contrato congelado, NO duplicar la fórmula)
# ================================================================================

@pytest.mark.anyio
async def test_matematica_deuda_pago_endpoint_interes_principal_saldo(client):
    """CONTRATO MATH: 1.000.000 · 2% EM · cuota 100.000 → 20.000 / 80.000 / 920.000."""
    headers = await _register(client, "c1_math_a@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)

    payment = await _pay_debt_endpoint(client, headers, debt["id"])

    assert payment["amount"] == MIN_PAYMENT
    assert payment["interest"] == INTEREST
    assert payment["principal"] == PRINCIPAL
    assert await _debt_balance(client, headers, debt["id"]) == Decimal(NEW_BALANCE)


@pytest.mark.anyio
async def test_matematica_deuda_pago_desde_evento_mismos_numeros(client):
    """CONTRATO MATH: la ruta del calendario produce exactamente los mismos números."""
    headers = await _register(client, "c1_math_b@example.com")
    await _create_account(client, headers, "1000000")
    debt = await _create_debt(client, headers)
    event = await _debt_event(client, headers)

    await _pay_event(client, headers, event["id"])

    payments = await client.get(f"/api/v1/debts/{debt['id']}/payments", headers=headers)
    assert payments.status_code == 200, payments.text
    rows = payments.json()
    assert len(rows) == 1
    assert rows[0]["interest"] == INTEREST
    assert rows[0]["principal"] == PRINCIPAL
    assert await _debt_balance(client, headers, debt["id"]) == Decimal(NEW_BALANCE)


@pytest.mark.anyio
async def test_matematica_deuda_ambas_rutas_son_identicas(client):
    """CONTRATO MATH: refactorizar el cálculo no puede cambiar los resultados."""
    headers_a = await _register(client, "c1_math_c_a@example.com")
    await _create_account(client, headers_a, "1000000")
    debt_a = await _create_debt(client, headers_a)
    await _pay_debt_endpoint(client, headers_a, debt_a["id"])
    pay_a = (await client.get(f"/api/v1/debts/{debt_a['id']}/payments", headers=headers_a)).json()[0]
    balance_a = await _debt_balance(client, headers_a, debt_a["id"])

    headers_b = await _register(client, "c1_math_c_b@example.com")
    await _create_account(client, headers_b, "1000000")
    debt_b = await _create_debt(client, headers_b)
    event_b = await _debt_event(client, headers_b)
    await _pay_event(client, headers_b, event_b["id"])
    pay_b = (await client.get(f"/api/v1/debts/{debt_b['id']}/payments", headers=headers_b)).json()[0]
    balance_b = await _debt_balance(client, headers_b, debt_b["id"])

    assert pay_a["interest"] == pay_b["interest"] == INTEREST
    assert pay_a["principal"] == pay_b["principal"] == PRINCIPAL
    assert balance_a == balance_b == Decimal(NEW_BALANCE)


# ================================================================================
# 8. G-7 — unpay (documentado, pendiente de decisión arquitectónica)
# ================================================================================

@pytest.mark.xfail(
    reason=(
        "DECISIÓN ARQUITECTÓNICA PENDIENTE — G-7: `unpay` hoy revierte deuda y evento "
        "pero deja la Transaction viva y el saldo de cuenta descontado. Antes de "
        "implementar hay que decidir (ADR): (i) borrar la Transaction vía "
        "TransactionService.delete, (ii) escribir un asiento compensador, o (iii) "
        "prohibir unpay cuando exista dinero ejecutado. El test sólo exige la "
        "invariante financiera (efecto neto 0 + saldo restaurado) sin prescribir mecanismo."
    ),
    strict=False,
)
@pytest.mark.anyio
async def test_g7_unpay_debe_dejar_el_dinero_consistente(client, session):
    """CONTRATO G-7: anular un pago no puede dejar dinero ejecutado huérfano.

    Escenario: cobro real desde calendario → Transaction + saldo debitado → `unpay`.
    Invariante esperado: efecto neto del ciclo = 0 y saldo de cuenta restaurado.
    Hoy: la Transaction sigue activa y la cuenta queda 45.000 más baja.
    """
    headers = await _register(client, "c1_g7@example.com")
    account = await _create_account(client, headers, "1000000")
    rp = await _create_recurring(
        client, headers,
        name="Ciclo G7", account_id=account["id"],
        day_of_month=date.today().day, next_due_date=date.today(),
    )
    event = await _pending_event(client, headers, rp["id"])

    await _pay_event(client, headers, event["id"])
    assert await _account_balance(client, headers, account["id"]) == Decimal(
        ACCOUNT_AFTER_RECURRING
    ), "precondición: el cobro debitó la cuenta"

    r = await client.post(f"/api/v1/events/{event['id']}/unpay", headers=headers)
    assert r.status_code == 200, r.text

    # 1) El saldo de cuenta vuelve al valor anterior al cobro
    assert await _account_balance(client, headers, account["id"]) == Decimal("1000000.00"), (
        "CONTRATO G-7: tras `unpay` la cuenta debe restaurarse; hoy queda en "
        f"{await _account_balance(client, headers, account['id'])} con la Transaction viva."
    )

    # 2) El efecto neto del ciclo sobre el dinero debe ser cero
    txs = await _db_transactions(session)
    cycle_txs = [t for t in txs if t["recurring_payment_id"] == rp["id"]]
    net = sum(
        (t["amount"] if t["type"] == "income" else -t["amount"]) for t in cycle_txs
    )
    assert net == Decimal("0"), (
        "CONTRATO G-7: `unpay` debe anular el efecto monetario del ciclo; "
        f"efecto neto actual {net} con {len(cycle_txs)} transacción(es) sin reversar."
    )
