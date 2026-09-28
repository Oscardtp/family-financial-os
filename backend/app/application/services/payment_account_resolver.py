"""Política única de fuente de fondos para pagos de deuda (FASE 6.4C-C2b, G-1).

Una sola función es invocada por la ruta directa (`DebtService.create_payment`)
y por la ruta de calendario (`CalendarDebtSyncService.on_event_paid`): cero
divergencia entre ambas y ninguna segunda autoridad de saldo.

Orden de resolución aprobado:

1. ``Debt.account_id`` — si existe, validado contra el hogar.
2. Cuenta por defecto del hogar.
3. Única cuenta activa del hogar (si sólo existe una).
4. Ninguna aplica ⇒ ``FundingSourceError`` ANTES del efecto monetario.

Nota de compatibilidad: ``AccountModel`` no expone ``is_default`` /
``is_primary`` (models.py:35-52) y añadir esa columna exigiría una migración,
fuera de alcance en C2b. Por eso el paso 2 se materializa como "la única cuenta
activa del hogar", que produce el mismo resultado mientras el hogar tenga una
sola cuenta — el caso de toda deuda histórica creada antes de C2b.

El fallback **sólo resuelve la cuenta**: nunca escribe ``Debt.account_id``
(no hay backfill silencioso) y nunca muta ``Account.balance``. La mutación
monetaria sigue siendo responsabilidad exclusiva de ``TransactionService``.
"""


class FundingSourceError(ValueError):
    """No hay una cuenta válida donde descontar el pago de la deuda."""


async def resolve_payment_account(debt: dict, household_id: str, account_repo) -> str:
    """Devuelve la ``account_id`` que financia el pago de ``debt`` en ``household_id``.

    Lanza ``FundingSourceError`` sin haber producido ningún efecto si no existe
    una cuenta válida.
    """
    account_id = debt.get("account_id")
    if account_id:
        account = await account_repo.get_by_id(account_id)
        if not account:
            raise FundingSourceError("La cuenta asociada a la deuda ya no existe")
        if account.get("household_id") != household_id:
            raise FundingSourceError(
                "La cuenta asociada a la deuda no pertenece a este hogar"
            )
        if not account.get("is_active", True):
            raise FundingSourceError("La cuenta asociada a la deuda está inactiva")
        return str(account["id"])

    active = [
        account
        for account in await account_repo.get_all(household_id)
        if account.get("is_active", True)
    ]
    if len(active) == 1:
        return str(active[0]["id"])
    if not active:
        raise FundingSourceError(
            "El hogar no tiene una cuenta activa donde descontar el pago"
        )
    raise FundingSourceError(
        "La deuda no tiene account_id y el hogar tiene varias cuentas: "
        "asigna una cuenta a la deuda antes de pagar"
    )
