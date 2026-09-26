"""FASE 6.4C-B — SSOT de next_due_date (Ownership + Compatibility Mirror).

Contrato congelado por el ADR de la FASE 6.4C-A y la decisión de arquitecto
de la FASE 6.4C-B:

| Concepto                    | Dueño                                    |
|-----------------------------|------------------------------------------|
| Próximo vencimiento (semántico) | FinancialObligation (frequency/anchor_day) |
| Cálculo                     | NextDueDateService (Application, único)  |
| Persistencia del espejo     | RecurringPayment.next_due_date           |
| Lectura Dashboard           | Permitida                                |
| Lectura API/Schemas         | Permitida                                |
| Lectura Repository/Engine   | Permitida                                |

`RecurringPayment.next_due_date` deja de ser dueño del cálculo y queda como
espejo persistente de compatibilidad: solo este servicio puede escribirlo.

La fórmula es EXACTAMENTE la histórica congelada por los Characterization
Tests (test_characterization_6_4b.py y test_recurring_payment_execution.py).
No se modifica: cambiarla rompe los 305 tests.
"""
from calendar import monthrange
from datetime import date, timedelta


class NextDueDateService:
    """Único punto autorizado de cálculo y escritura de next_due_date."""

    @staticmethod
    def calculate(frequency: str, anchor_day: int, base_date: date) -> date:
        """Calcula el próximo vencimiento con la fórmula histórica congelada.

        `anchor_day` es `day_of_month` en RecurringPayment y `anchor_day`
        en FinancialObligation: el mismo concepto (día de la cadencia).
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

    @staticmethod
    def ensure_initial(payload: dict, base_date: date | None = None) -> dict:
        """Completa el espejo en la creación del registro (E1), si no fue provisto.

        Si el cliente entrega `next_due_date`, se respeta sin recalcular
        (contrato de API existente). Si no, se calcula con la fórmula
        congelada. Único punto que gobierna el valor al nacer el espejo.
        """
        if not payload.get("next_due_date"):
            payload["next_due_date"] = NextDueDateService.calculate(
                payload.get("frequency", "monthly"),
                payload.get("day_of_month", 1),
                base_date or date.today(),
            )
        return payload

    @staticmethod
    async def persist_mirror(repo, recurring: dict, base_date: date | None = None) -> dict:
        """Escribe el espejo persistente `RecurringPayment.next_due_date`.

        Único escritor autorizado de la capa Application. `repo` es el
        repositorio de pagos recurrentes (Dependency Injection).
        """
        next_due = NextDueDateService.calculate(
            recurring.get("frequency", "monthly"),
            recurring.get("day_of_month", 1),
            base_date or date.today(),
        )
        return await repo.update({**recurring, "next_due_date": next_due})
