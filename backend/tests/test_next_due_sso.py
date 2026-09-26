"""FASE 6.4C-B — SSOT de next_due_date (Ownership + Compatibility Mirror).

Congela tres contratos del ADR 6.4C-A/6.4C-B:

1. La fórmula del próximo vencimiento es EXACTAMENTE la histórica
   (la congelada por test_characterization_6_4b.py y
   test_recurring_payment_execution.py).
2. Existe un único escritor persistente en la capa Application.
3. event_service y recurring_payment_service delegan; no calculan.
"""
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parents[1] / "app"
APPLICATION_ROOT = APP_ROOT / "application"


def _read(rel_path: str) -> str:
    return (APP_ROOT / rel_path).read_text(encoding="utf-8")


def _legacy_reference_next_due(frequency, anchor_day, base_date):
    """Copia congelada de la fórmula histórica.

    Es la implementación original que vivía en
    RecurringPaymentService._calculate_next_due y era duplicada en
    FinancialEventService._create_transaction_for_recurring_event.
    No se modifica: funciona como referencia congelada del comportamiento.
    """
    if frequency == "weekly":
        return base_date + timedelta(weeks=1)
    if frequency == "biweekly":
        return base_date + timedelta(weeks=2)
    if frequency == "monthly":
        next_month = base_date.month + 1
        next_year = base_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        max_day = monthrange(next_year, next_month)[1]
        return date(next_year, next_month, min(anchor_day, max_day))
    if frequency == "yearly":
        max_day = monthrange(base_date.year + 1, base_date.month)[1]
        return date(base_date.year + 1, base_date.month, min(anchor_day, max_day))
    return base_date + timedelta(days=30)


FROZEN_CASES = [
    ("weekly", 1, date(2026, 9, 25)),
    ("biweekly", 1, date(2026, 9, 25)),
    ("monthly", 15, date(2026, 9, 25)),
    ("monthly", 31, date(2026, 10, 31)),
    ("monthly", 31, date(2026, 12, 15)),
    ("monthly", 1, date(2026, 12, 31)),
    ("monthly", 30, date(2026, 1, 31)),
    ("monthly", 29, date(2026, 2, 28)),
    ("yearly", 29, date(2026, 2, 10)),
    ("yearly", 31, date(2026, 7, 4)),
    ("quarterly", 5, date(2026, 9, 25)),
    (None, 5, date(2026, 9, 25)),
]

FROZEN_EXPECTED = [
    date(2026, 10, 2),
    date(2026, 10, 9),
    date(2026, 10, 15),
    date(2026, 11, 30),
    date(2027, 1, 31),
    date(2027, 1, 1),
    date(2026, 2, 28),
    date(2026, 3, 29),
    date(2027, 2, 28),
    date(2027, 7, 31),
    date(2026, 10, 25),
    date(2026, 10, 25),
]


def test_owner_lives_in_application_layer():
    """El único escritor es un servicio especializado de Application."""
    owner = APPLICATION_ROOT / "services" / "next_due_service.py"
    assert owner.is_file(), (
        "6.4C-B: falta el propietario único de next_due_date en "
        "app/application/services/next_due_service.py"
    )


@pytest.mark.parametrize(
    "frequency,anchor_day,base_date", FROZEN_CASES,
    ids=[f"{f}-{d}-{b.isoformat()}" for f, d, b in FROZEN_CASES],
)
def test_formula_is_identical_to_frozen_reference(frequency, anchor_day, base_date):
    """La fórmula nueva debe producir EXACTAMENTE la salida histórica."""
    from app.application.services.next_due_service import NextDueDateService

    got = NextDueDateService.calculate(frequency, anchor_day, base_date)
    expected = _legacy_reference_next_due(frequency, anchor_day, base_date)
    assert got == expected, (
        "6.4C-B: la fórmula de next_due_date cambió "
        f"({frequency}, día {anchor_day}, base {base_date}): {got} != {expected}"
    )


@pytest.mark.parametrize(
    "case,expected",
    list(zip(FROZEN_CASES, FROZEN_EXPECTED)),
    ids=[f"{f}-{d}-{b.isoformat()}" for f, d, b in FROZEN_CASES],
)
def test_formula_known_frozen_values(case, expected):
    """Valores absolutos congelados (verificados contra el código histórico)."""
    from app.application.services.next_due_service import NextDueDateService

    frequency, anchor_day, base_date = case
    assert NextDueDateService.calculate(frequency, anchor_day, base_date) == expected


def test_application_layer_has_single_persistent_writer():
    """Único escritor persistente: solo next_due_service.py escribe el espejo."""
    offenders = []
    for path in sorted(APPLICATION_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "next_due_date" in source and "update(" in source:
            offenders.append(path.relative_to(APPLICATION_ROOT).as_posix())
    assert offenders == ["services/next_due_service.py"], (
        "6.4C-B: la capa Application debe tener UN solo escritor de "
        f"next_due_date; se encontraron: {offenders}"
    )


def test_event_service_delegates_and_no_longer_calculates():
    """event_service eliminó la copia de la fórmula (E4) y delega."""
    source = _read("application/services/event_service.py")
    assert "monthrange" not in source, (
        "6.4C-B: event_service aún contiene una copia de la fórmula mensual"
    )
    assert "next_due_date" not in source, (
        "6.4C-B: event_service aún calcula/escribe next_due_date en lugar de delegar"
    )
    assert "NextDueDateService" in source, (
        "6.4C-B: event_service debe delegar en el propietario único"
    )


def test_recurring_payment_service_delegates_and_no_longer_calculates():
    """recurring_payment_service (E1/E2/E3) delega; desaparece _calculate_next_due."""
    source = _read("application/services/recurring_payment_service.py")
    assert "_calculate_next_due" not in source, (
        "6.4C-B: RecurringPaymentService aún define su propio cálculo"
    )
    assert "monthrange" not in source, (
        "6.4C-B: RecurringPaymentService aún importa la lógica de la fórmula"
    )
    assert "NextDueDateService" in source, (
        "6.4C-B: RecurringPaymentService debe delegar en el propietario único"
    )


def test_readers_are_untouched():
    """Los lectores declarados no cambian: dashboard, repositorio, schemas, engine."""
    readers = {
        "application/services/dashboard_service.py": "next_due_date",
        "infrastructure/repositories/recurring_payment_repository.py": "next_due_date",
        "financial_engine/calendar_engine.py": "next_due_date",
        "presentation/schemas/schemas.py": "next_due_date",
        "infrastructure/models/models.py": "next_due_date",
    }
    for rel_path, token in readers.items():
        assert token in _read(rel_path), (
            f"6.4C-B: el lector {rel_path} dejó de exponer {token}"
        )
