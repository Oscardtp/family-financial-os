# Domain Rules (Financial Engine)

Reglas de negocio del núcleo financiero. El *Financial Engine* vive en `modules/` y
`shared/` (pura, sin infra) — por eso es testeable sin base de datos.

## Entidades & Value Objects

- `Money` — VO basado en Dinero.js v2: `amount: bigint` + `currency: string` (ISO 4217). Operaciones: add/subtract/match (requiere currency igual). Nunca expone `number` para cálculo.
- `Account` — entidad `FinancialAccount` (id, userId, name, currency, type: checking|savings|cash|credit_card|loan|investment|...) con **tipo de flujo** (asset o liability).
- `Transaction` (+ asientos `LedgerLine`) — entidad. Tipo: Income | Expense | Transfer | Adjustment. Fecha, importe, cuenta(s) afectada(s).
- `Budget` / `Goal` — objetivo de ahorro con target date y amount.

## Invariantes (forzables por tests)

### D1. Double-entry (doble entrada)
- Cada `Transaction` contiene ≥ 2 `LedgerLine` (debito/crédito) y la suma de débitos = suma de créditos en la misma moneda.
- El motor rechaza el lote si no cuadra (doble entrada o nada).
- Tipo `Income`/`Expense` (1 línea contra cuenta + 1 contra income/expense rollup) y `Transfer` (2 líneas entre cuentas propias).

### D2. Money matching
- No se suman/restan `Money` de distinta moneda → `match currency` o se lanza `CurrencyMismatchError`.

### D3. Transferencia ≠ Gasto
- `Transfer` redistribuye patrimonio (account A débito, account B crédito; patrimonio neto inalterado).
- `Expense` reduce patrimonio; `Income` lo incrementa.

### D4. Tipo de cuenta (normal/reversa)
- Assets & Expenses: saldo normal DEBEBITO.
  - Liabilities, Income, Equity: saldo normal CRÉDITO.
- El *rollup* del P&L y Balance aplica el signo correcto en función del tipo.

### D5. Saldo = suma de asientos
- `account.balance = Σ(line.amount) * signo_de_tipo_de_cuenta`. Nunca se escribe a mano; siempre se deriva.

### D6. UUID v7 & append-only
- IDs cronológicos (UUID v7). Transacciones imposibles de borrar: anulación = nueva transacción de corrección referenciando la original.

### D7. Conciliación bancaria
- Cada transición de estado de conciliación necesita trazabilidad (import_id, transaction_id, status).

### D8. Reportes derivados
- Net Worth = Σ(activos) − Σ(pasivos) recalculado sobre saldos.
- P&L período = ingresos − gastos netos del período.

## Autorización
- Todo acceso a datos se filtra por `userId` (proveniente de Supabase Auth → `UserId` branded en dominio). La capa de repositorio SIEMPRE incluye `WHERE user_id = ?`. Nunca se filtra solo por cliente.

## Precisión
- Redondeos: bancario (ROUND_HALF_EVEN) sobre bigint de centavos; nunca sobre float.
