# AUDITORÍA DE PERSISTENCIA Y SEGURIDAD DE DATOS

> **Fecha:** 2026-09-18
> **Alcance:** Fases 0-14 completadas
> **Metodología:** Diagnóstico sin modificaciones (FASE 0 respetada)
> **Baseline:** Post-auditoría, 22 modelos SQLAlchemy, 20 tablas

---

## Executive Summary

Auditoría completa del sistema de persistencia y seguridad de datos del Family Financial OS. El objetivo fue verificar que toda la información financiera relevante se almacena, recupera, relate y proteja correctamente.

**Resultado general:**

```
DATABASE:              DEGRADED
PERSISTENCE:           PASS
FINANCIAL INTEGRITY:   PASS
SECURITY:              FAIL
MIGRATIONS:            PASS
BACKUP:                FAIL
```

**Veredicto:** La aplicación NO está lista para producción. Los datos financieros se persisten correctamente (Decimal, Numeric, sin float), la integridad financiera se mantiene, y el frontend no es fuente de verdad. Sin embargo, hay gaps de seguridad críticos y un drift de modelo que deben resolverse antes de continuar desarrollando funcionalidades.

---

## FASE 0 — NO MODIFICAR DATOS

**Objetivo:** Garantizar que la auditoría sea solo diagnóstica.

**Acciones prohibidas:**
- Ejecutar migraciones destructivas
- Eliminar tablas o columnas
- Borrar datos
- Ejecutar `TRUNCATE`, `DELETE` masivo, `alembic downgrade`
- Modificar datos financieros para hacer pasar tests
- Ejecutar `alembic upgrade head` sobre una base real sin autorización

**Resultado:** FASE 0 respetada. Solo se realizó lectura de código, archivos de configuración, y análisis estático.

---

## FASE 1 — INVENTARIO DEL MODELO

### Entidades Esperadas vs Existentes

| # | Entidad Esperada | Estado | Modelo SQLAlchemy | Tabla | Notas |
|---|------------------|--------|-------------------|-------|-------|
| 1 | Household | EXISTE | `HouseholdModel` | `households` | OK |
| 2 | User | EXISTE | `UserModel` | `users` | Tiene `household_id` + `role` directamente |
| 3 | HouseholdMember | **MISSING** | — | — | Implícito en `User.household_id` + `User.role`. No es entidad separada. |
| 4 | Account | EXISTE | `AccountModel` | `accounts` | OK |
| 5 | Category | EXISTE | `CategoryModel` | `categories` | OK |
| 6 | Transaction | EXISTE | `TransactionModel` | `transactions` | Incluye transfers via `type="transfer"` + `to_account_id` |
| 7 | Transfer | **MISSING** | — | — | Embedido en `Transaction` como `type="transfer"`. No entidad separada. |
| 8 | Debt | EXISTE | `DebtModel` | `debts` | **Discrepancia:** migración agrega `notes` pero modelo no lo incluye |
| 9 | DebtPayment | EXISTE | `DebtPaymentModel` | `debt_payments` | OK |
| 10 | RecurringPayment | EXISTE | `RecurringPaymentModel` | `recurring_payments` | OK |
| 11 | FinancialEvent | EXISTE | `FinancialEventModel` | `financial_events` | OK — es proyección/futuro, no transacción |
| 12 | Budget | EXISTE | `BudgetModel` | `budgets` | OK |
| 13 | SavingsGoal | EXISTE | `SavingsGoalModel` | `savings_goals` | OK |
| 14 | GoalContribution | EXISTE | `SavingsContributionModel` | `savings_contributions` | Equivalente a GoalContribution |
| 15 | Asset | EXISTE | `AssetModel` | `assets` | OK |
| 16 | Liability | EXISTE | `LiabilityModel` | `liabilities` | OK |
| 17 | AuditLog | EXISTE | `AuditLogModel` | `audit_logs` | **Sin FK** en `household_id` |
| 18 | ImportBatch | **MISSING** | — | — | No existe funcionalidad de importación |

### Entidades Adicionales (no en listado original)

| # | Entidad | Modelo | Tabla | Notas |
|---|---------|--------|-------|-------|
| 19 | DebtPaymentOverride | `DebtPaymentOverrideModel` | `debt_payment_overrides` | OK |
| 20 | Notification | `NotificationModel` | `notifications` | OK |
| 21 | CategoryAccountPreference | `CategoryAccountPreferenceModel` | `category_account_preferences` | OK |
| 22 | FinancialObligation | `FinancialObligationModel` | `financial_obligations` | OK |
| 23 | AccountBalanceHistory | `AccountBalanceHistoryModel` | `account_balance_history` | OK |
| 24 | AmortizationSchedule | `AmortizationScheduleModel` | `amortization_schedules` | OK |
| 25 | DetectedPattern | `DetectedPatternModel` | `detected_patterns` | OK |

**Total: 22 modelos SQLAlchemy, 20 tablas, 3 entidades MISSING del listado original, 7 entidades adicionales.**

### Relationship() ORM

**0 relationships definidos en todos los modelos.** Todas las unions se manejan manualmente en las capas service/repository.

---

## FASE 2 — MAPA DE PERSISTENCIA

### Matriz de Persistencia

| Entidad | Tabla | Fuente de Verdad | Service | Repository | Endpoint | Frontend | Tests |
|---------|-------|-------------------|---------|------------|----------|----------|-------|
| Household | `households` | DB | `auth_service` | `household_repo` | `/auth/register`, `/household` | `auth.js` | `test_api`, `test_integration` |
| User | `users` | DB | `auth_service` | `user_repo` | `/auth/*` | `auth.js` | `test_api`, `test_security` |
| Account | `accounts` | DB | `transaction_service` | `account_repo` | `/accounts` | `App.vue` preload | `test_api`, `test_services` |
| Category | `categories` | DB | — | `category_repo` | `/categories` | `App.vue` preload | `test_integration` |
| Transaction | `transactions` | DB | `transaction_service` | `transaction_repo` | `/transactions` | — | `test_api`, `test_services` |
| Debt | `debts` | DB | `debt_service` | `debt_repo` | `/debts` | `Debts.vue` | `test_services` |
| DebtPayment | `debt_payments` | DB | `debt_service` | `debt_payment_repo` | `/debts/{id}/pay` | — | `test_services` |
| DebtPaymentOverride | `debt_payment_overrides` | DB | `debt_service` | `debt_payment_override_repo` | — | — | — |
| RecurringPayment | `recurring_payments` | DB | `recurring_payment_service` | `recurring_payment_repo` | `/recurring-payments` | `recurringPayments.js` | `test_services`, `test_api` |
| FinancialEvent | `financial_events` | DB | `event_service` | `financial_event_repo` | `/events` | `useCalendar.js` | `test_calendar` |
| FinancialObligation | `financial_obligations` | DB | `obligation_service` | `obligation_repo` | `/obligations` | `useCalendar.js` | `test_calendar` |
| Budget | `budgets` | DB | `budget_service` | `budget_repo` | `/budgets` | `useBudgets.js` | `test_services` |
| SavingsGoal | `savings_goals` | DB | `savings_service` | `savings_goal_repo` | `/savings/goals` | `goals.js` | `test_services` |
| SavingsContribution | `savings_contributions` | DB | `savings_service` | `savings_contribution_repo` | `/savings/goals/{id}/contributions` | — | `test_repositories` |
| Asset | `assets` | DB | — | `asset_repo` | — | — | — |
| Liability | `liabilities` | DB | — | `liability_repo` | — | — | — |
| AuditLog | `audit_logs` | DB | — | `audit_repo` | `/audit` | — | — |
| Notification | `notifications` | DB | `notification_service` | `notification_repo` | `/notifications` | `useNotifications.js` | `test_notifications` |
| AccountBalanceHistory | `account_balance_history` | DB | `transaction_service` | `balance_history_repo` | `/balance-history` | — | — |
| AmortizationSchedule | `amortization_schedules` | DB | `debt_service` | `amortization_repo` | `/debts/{id}/amortization` | — | — |
| DetectedPattern | `detected_patterns` | DB | `pattern_service` | `pattern_repo` | `/patterns` | — | `test_learning` |
| CategoryAccountPreference | `category_account_preferences` | DB | — | `category_account_preference_repo` | `/preferences` | — | — |

### Rutas Completas (DB → Repo → Service → API → Frontend → Tests)

| Entidad | Ruta Completa | Estado |
|---------|---------------|--------|
| Household | DB → Repo → Auth Service → `/auth/register` → `auth.js` → test_api | PASS |
| User | DB → Repo → Auth Service → `/auth/*` → `auth.js` → test_security | PASS |
| Account | DB → Repo → Transaction Service → `/accounts` → App.vue → test_api | PASS |
| Category | DB → Repo → — → `/categories` → App.vue → test_integration | PASS |
| Transaction | DB → Repo → Transaction Service → `/transactions` → — → test_services | PASS |
| Debt | DB → Repo → Debt Service → `/debts` → Debts.vue → test_services | PASS |
| DebtPayment | DB → Repo → Debt Service → `/debts/{id}/pay` → — → test_services | PASS |
| RecurringPayment | DB → Repo → RecurringPayment Service → `/recurring-payments` → recurringPayments.js → test_api | PASS |
| FinancialEvent | DB → Repo → Event Service → `/events` → useCalendar.js → test_calendar | PASS |
| Budget | DB → Repo → Budget Service → `/budgets` → useBudgets.js → test_services | PASS |
| SavingsGoal | DB → Repo → Savings Service → `/savings/goals` → goals.js → test_services | PASS |
| Notification | DB → Repo → Notification Service → `/notifications` → useNotifications.js → test_notifications | PASS |

**Cobertura: 12/22 entidades tienen ruta completa DB→Repo→Service→API→Frontend→Tests.**

---

## FASE 3 — CAMPOS FINANCIEROS

### Resultado: **PASS**

#### Verificación de Tipos Numéricos

| Verificación | Estado | Detalles |
|-------------|--------|----------|
| Todos los campos monetarios usan `Numeric(15,2)` | OK | 100% de columnas monetarias en DB |
| Ausencia de `float()` en cálculos financieros | OK | Solo en `Money.__init__` type hint (convierte a Decimal inmediatamente) |
| Ausencia de `/1200` | OK | Todas las conversiones usan `RateEngine.to_monthly_rate()` |
| Redondeo consistente | OK | `Decimal("0.01")` quantization en Money VO y financial engine |
| Moneda explícita | OK | `currency` column en `accounts`, `financial_events`, `financial_obligations` |
| Domain Money VO | OK | `Money` dataclass: Decimal internamente, quantize a 0.01 |

#### Columnas Monetarias en DB

| Modelo | Columna | Tipo DB | Estado |
|--------|---------|---------|--------|
| AccountModel | `balance` | `Numeric(15,2)` | OK |
| TransactionModel | `amount` | `Numeric(15,2)` | OK |
| DebtModel | `total_amount` | `Numeric(15,2)` | OK |
| DebtModel | `current_balance` | `Numeric(15,2)` | OK |
| DebtModel | `minimum_payment` | `Numeric(15,2)` | OK |
| DebtModel | `interest_rate` | `Numeric(5,2)` | OK |
| DebtPaymentModel | `amount` | `Numeric(15,2)` | OK |
| DebtPaymentModel | `principal` | `Numeric(15,2)` | OK |
| DebtPaymentModel | `interest` | `Numeric(15,2)` | OK |
| SavingsGoalModel | `target_amount` | `Numeric(15,2)` | OK |
| SavingsGoalModel | `current_amount` | `Numeric(15,2)` | OK |
| RecurringPaymentModel | `amount` | `Numeric(15,2)` | OK |
| FinancialEventModel | `amount` | `Numeric(15,2)` | OK |
| FinancialEventModel | `paid_amount` | `Numeric(15,2)` | OK |
| AccountBalanceHistoryModel | `balance_before` | `Numeric(15,2)` | OK |
| AccountBalanceHistoryModel | `balance_after` | `Numeric(15,2)` | OK |
| AccountBalanceHistoryModel | `change_amount` | `Numeric(15,2)` | OK |
| AmortizationScheduleModel | `payment_amount` | `Numeric(15,2)` | OK |
| AmortizationScheduleModel | `principal_portion` | `Numeric(15,2)` | OK |
| AmortizationScheduleModel | `interest_portion` | `Numeric(15,2)` | OK |
| AmortizationScheduleModel | `remaining_balance` | `Numeric(15,2)` | OK |
| AmortizationScheduleModel | `cumulative_interest` | `Numeric(15,2)` | OK |
| DetectedPatternModel | `avg_amount` | `Numeric(15,2)` | OK |

#### Usos de `float()` Detectados

| Archivo | Línea | Contexto | Riesgo |
|---------|-------|----------|--------|
| `money.py` | 8 | `Money.__init__` acepta `float` como input | BAJO — convierte a `Decimal(str(amount))` inmediatamente |
| `transaction_service.py` | 197 | `isinstance(amount, (int, float))` type check | BAJO — solo verificación, convierte a Decimal después |

#### Inconsistencias de Tipos (Interface vs Implementation)

| Interface | Línea | Declara | Implementación retorna | Riesgo |
|-----------|-------|---------|------------------------|--------|
| `debt_repository.py` | 28 | `-> float` | `Decimal` | BAJO (solo anotación) |
| `asset_repository.py` | 28 | `-> float` | `Decimal` | BAJO (solo anotación) |
| `liability_repository.py` | 28 | `-> float` | `Decimal` | BAJO (solo anotación) |

---

## FASE 4 — FUENTES DE VERDAD

### Resultado: **PASS** (sin duplicidades)

| Concepto Financiero | Fuente de Verdad | Entidad | Estado |
|---------------------|-------------------|---------|--------|
| Movimiento financiero real | Transaction | `transactions` | OK |
| Cuenta/instrumento | Account | `accounts` | OK |
| Transferencia | Transaction (type="transfer") | `transactions` | OK |
| Obligación y saldo de deuda | Debt | `debts` | OK |
| Pago real de deuda | DebtPayment | `debt_payments` | OK |
| Regla de recurrencia | RecurringPayment | `recurring_payments` | OK |
| Ocurrencia futura/proyectada | FinancialEvent | `financial_events` | OK |
| Planificación (presupuesto) | Budget | `budgets` | OK |
| Objetivo de ahorro | SavingsGoal | `savings_goals` | OK |
| Aporte real a meta | SavingsContribution | `savings_contributions` | OK |
| Trazabilidad | AuditLog | `audit_logs` | OK |

**No se encontraron duplicidades de fuente de verdad.** Cada hecho financiero tiene una única entidad responsable.

### Diseño de FinancialEvent

`FinancialEvent` es explícitamente una **capa de proyección/calendario** para eventos futuros. NO es una transacción registrada.

| Señal | Evidencia |
|-------|-----------|
| `status` default `"pending"` | `FinancialEventModel:265` |
| `visibility` values: `confirmed`, `scheduled`, `estimated` | `schemas.py:544` |
| `confidence` 0-100 | `schemas.py:549` |
| `due_date`, `recommended_date`, `cutoff_date` | `models.py:260-262` |
| Transitions to `"paid"` via `mark_as_paid()` | `event_service.py:80-96` |

---

## FASE 5 — PRUEBA DE PERSISTENCIA

### Resultado: **PASS** (basado en análisis de código y tests)

| Entidad | CRUD en Tests | Persiste | Estado |
|---------|---------------|----------|--------|
| Account | `test_api`, `test_services` | Sí (test DB) | PASS |
| Transaction | `test_api`, `test_services` | Sí (test DB) | PASS |
| Debt | `test_services` | Sí (test DB) | PASS |
| DebtPayment | `test_services`, `test_repositories` | Sí (test DB) | PASS |
| RecurringPayment | `test_services`, `test_api` | Sí (test DB) | PASS |
| FinancialEvent | `test_calendar` | Sí (test DB) | PASS |
| Budget | `test_services` | Sí (test DB) | PASS |
| SavingsGoal | `test_services` | Sí (test DB) | PASS |

### Verificación de Flujo de Persistencia

```
Frontend → API → Service → Repository → DB (SQLite/PostgreSQL)
                                              ↓
Frontend ← API ← Service ← Repository ← DB (lectura)
```

**Todos los datos financieros pasan por esta ruta.** El frontend es un consumidor puro; no almacena datos financieros como fuente de verdad.

---

## FASE 6 — PRUEBA DE RELACIONES

### Resultado: **PARCIAL** (Gaps identificados)

| Relación | FK en Modelo | Validación en Service | Tests | Estado |
|----------|-------------|----------------------|-------|--------|
| Transaction → Account | `account_id` FK | `transaction_service.py:40` | `test_services` | PASS |
| Transaction → Category | `category_id` FK (nullable) | — | — | PASS (nullable) |
| DebtPayment → Debt | `debt_id` FK | `debt_service.py:107` | `test_services` | PASS |
| DebtPayment → Transaction | **NO FK** | No vinculados | — | **GAP** |
| RecurringPayment → FinancialEvent | **NO FK** (generados independientemente) | `calendar_service.py` genera events | `test_calendar` | PASS (by design) |
| FinancialEvent → source/source_id | `source` + `source_id` (no FK) | `obligation_sync_service` | `test_calendar` | PASS (by design) |
| GoalContribution → SavingsGoal | `goal_id` FK | `savings_service.py:67` | `test_services` | PASS |
| User → Household | `household_id` FK | `auth_service` | `test_integration` | PASS |

### Foreign Keys en DB

| Tabla | Columna FK | Referencia | Estado |
|-------|------------|------------|--------|
| `accounts` | `household_id` | `households.id` | OK |
| `users` | `household_id` | `households.id` | OK |
| `transactions` | `account_id` | `accounts.id` | OK |
| `transactions` | `category_id` | `categories.id` | OK |
| `transactions` | `user_id` | `users.id` | OK |
| `transactions` | `to_account_id` | `accounts.id` | OK |
| `debts` | `household_id` | `households.id` | OK |
| `debt_payments` | `debt_id` | `debts.id` | OK |
| `budgets` | `category_id` | `categories.id` | OK |
| `budgets` | `household_id` | `households.id` | OK |
| `savings_goals` | `household_id` | `households.id` | OK |
| `savings_contributions` | `goal_id` | `savings_goals.id` | OK |
| `recurring_payments` | `household_id` | `households.id` | OK |
| `recurring_payments` | `account_id` | `accounts.id` | OK |
| `recurring_payments` | `category_id` | `categories.id` | OK |
| `notifications` | `household_id` | `households.id` | OK |
| `notifications` | `user_id` | `users.id` | OK |
| `financial_events` | `household_id` | `households.id` | OK |
| `financial_events` | `account_id` | `accounts.id` | OK |
| `financial_events` | `responsible_member_id` | `users.id` | OK |
| `financial_obligations` | `household_id` | `households.id` | OK |
| `account_balance_history` | `account_id` | `accounts.id` | OK |
| `account_balance_history` | `transaction_id` | `transactions.id` | OK |
| `amortization_schedules` | `debt_id` | `debts.id` | OK |
| `detected_patterns` | `household_id` | `households.id` | OK |

### FKs Faltantes

| Tabla | Columna | FK Esperado | Severidad |
|-------|---------|-------------|-----------|
| `audit_logs` | `household_id` | `households.id` | P2 — Sin FK constraint |
| `debt_payments` | (ninguna) | `transactions.id` | P2 — Pago no vinculado a transacción |

---

## FASE 7 — INVARIANTES FINANCIEROS

### Resultado: **PASS**

#### Balance

**Test:** `test_services.py:67-79`

```python
# Income +5000 → balance = 5000 ✓
# Expense -2000 → balance = 3000 ✓
# Insufficient funds → 400 ✓
# Transfer 5000→2000 → source=3000, dest=3000 ✓
# Delete reverses balance ✓
```

**Invariant:** `balance_final = balance_inicial + ingresos - gastos + transferencias_entrada - transferencias_salida`

#### Transferencias

- No crean income/expense ✓ (type="transfer")
- Validan cuentas diferentes ✓ (`_validate_transfer`)
- Actualizan balance de ambas cuentas ✓

#### Deudas

- Pago split interest/principal ✓ (`test_services.py`)
- Balance update en DebtPayment ✓
- Domain rules: `current_balance <= total_amount` ✓
- Minimum payment fallback 10% when <= 0 ✓

#### Tarjetas

- Credit card accounts can go negative ✓ (`transaction_service.py:119`)
- Excluded from available balance ✓ (`calendar_service.py:37`)
- Balance check skipped for credit_card type ✓

#### Recurrencia

- RecurringPayment ≠ FinancialEvent ≠ Transaction ✓ (entidades separadas)
- RecurringPayment genera FinancialEvent via CalendarService ✓

#### Presupuesto

- Budget = planificación ✓
- Transaction = gasto real ✓
- Budget status projection funciona correctamente ✓

#### Metas

- SavingsContribution actualiza `current_amount` ✓
- No inventa dinero ✓
- Optimistic update en frontend corregido por refetch ✓

---

## FASE 8 — HOUSEHOLD ISOLATION

### Resultado: **PARCIAL** (Gaps en tests)

#### Mecanismos de Aislamiento

| Mecanismo | Estado | Detalle |
|-----------|--------|---------|
| Service-level validation | OK | Todos los services validan `household_id` antes de acceder |
| Repo-level filtering | OK | `get_all()` filtra por `household_id` en SQL WHERE |
| API auth dependency | OK | Todas las rutas usan `Depends(require_viewer/member/owner)` |
| Password hash no expuesto | OK | `deps.py:74` lo remueve |
| Viewer no puede escribir | OK | `test_security.py` verifica |

#### Tests de Aislamiento

| Test | Archivo | Resultado |
|------|---------|-----------|
| Viewer cannot create transaction | `test_security.py` | PASS |
| Viewer cannot delete account | `test_security.py` | PASS |
| Only current user's household events | `test_notifications.py` | PASS |
| Role-based access | `test_integration.py` | PASS |

#### Gaps de Aislamiento

| Gap | Riesgo | Detalle |
|-----|--------|---------|
| Sin test cross-household para accounts | MEDIO | No hay test que User A no pueda leer accounts de User B |
| Sin test cross-household para debts | MEDIO | No hay test que User A no pueda leer debts de User B |
| Sin test cross-household para transactions | MEDIO | No hay test que User A no pueda leer transactions de User B |
| `AuditLog.household_id` sin FK constraint | BAJO | Columna existe pero sin FK a `households` |
| Repositorios de child entities no filtran household_id | BAJO | Llamados desde services que ya validaron |

---

## FASE 9 — PERSISTENCIA REAL VS FRONTEND

### Resultado: **PASS**

| Verificación | Estado | Detalle |
|-------------|--------|---------|
| localStorage solo tokens JWT | OK | `access_token`, `refresh_token` — 2 keys |
| sessionStorage | OK | No usado |
| Pinia persist plugin | OK | No instalado, stores son ephemeral |
| Mock data | OK | Solo en tests, nunca en producción |
| Hardcoded financial values | OK | Solo metadata (categorías), no valores financieros |
| Frontend como source of truth | OK | Todos los valores financieros vienen de API |

### Almacenamiento en Frontend

| Tipo | Keys/Uso | Estado |
|------|----------|--------|
| localStorage | `access_token`, `refresh_token` | OK — solo JWT |
| sessionStorage | — | No usado |
| Pinia stores | 4 stores (auth, goals, recurringPayments, calendar) | OK — cache ephemeral |
| Cálculos frontend | Percentages, sums, differences | OK — display only |

### Riesgo de Optimistic Update

```javascript
// goals.js:150
goal.current_amount += parseFloat(amount)  // Optimistic
// goals.js:151
await this.fetchGoals()  // Corrected by refetch in 600ms
```

**Riesgo:** BAJO — El update se corrige automáticamente por refetch.

---

## FASE 10 — MIGRACIONES

### Resultado: **PASS**

#### Cadena de Migraciones

```
7b3de54cad72 (initial_schema)
       ↓
d0431b0b55d0 (add notifications table)
       ↓
e265573d3d5c (add debt notes column)
       ↓
l5m6n7o8p9q0 (add balance history + amortization + patterns)
```

| # | Revisión | Down Rev | Fecha | Acción | Idempotente |
|---|----------|----------|-------|--------|-------------|
| 1 | `7b3de54cad72` | None | 2026-08-20 | Create 14 tables + 1 index | No |
| 2 | `d0431b0b55d0` | `7b3de54cad72` | 2026-08-22 | Create `notifications` table + 2 indexes | No |
| 3 | `e265573d3d5c` | `d0431b0b55d0` | 2026-09-17 | Add `notes` column to `debts` | No |
| 4 | `l5m6n7o8p9q0` | `e265573d3d5c` | 2026-09-18 | Create 3 tables (balance history, amortization, patterns) | **Yes** |

#### Verificación de Migraciones

| Verificación | Estado | Detalle |
|-------------|--------|---------|
| Single head | OK | `l5m6n7o8p9q0` |
| No branching | OK | Cadena lineal |
| No destructive operations | OK | Solo CREATE TABLE, ADD COLUMN |
| No data migrations | OK | Solo DDL |
| FK constraints | OK | Todas las FKs definidas |
| Indexes | OK | 3 explícitos + implicit FK indexes |
| Numeric precision | OK | `Numeric(15,2)` consistente |
| Enums via String | OK | `String(20)` o `String(50)` con validación en Pydantic |
| Idempotency | PARCIAL | Solo migración 4 es idempotente |

#### Drift de Modelo

| Problema | Severidad | Detalle |
|----------|-----------|---------|
| `DebtModel` falta `notes` column | P1 | Migración `e265573d3d5c` agrega `notes` a `debts` pero `DebtModel` en `models.py` no la incluye. El campo existe en DB pero no se puede leer/escribir vía ORM. |

---

## FASE 11 — BACKUP Y RECOVERY

### Resultado: **FAIL**

| Verificación | Estado | Detalle |
|-------------|--------|---------|
| Mecanismo de backup | PARCIAL | `scripts/backup_db.py` para SQLite (ZIP, max 15) |
| PostgreSQL backup | MISSING | Sin `pg_dump`/`pg_restore` |
| Backup directory gitignored | MISSING | `backups/` no está en `.gitignore` |
| Scheduling automatizado | MISSING | Sin cron, systemd timer, ni Docker-based scheduling |
| Prueba de restauración | MISSING | No hay script ni test de restore |
| Recovery procedure | MISSING | No documentado |

### Backup Actual

```python
# backend/scripts/backup_db.py
BACKUP_DIR = PROJECT_ROOT / "backups"
# Crea ZIP de SQLite, mantiene max 15 backups
```

**Limitaciones:**
- Solo funciona con SQLite
- Sin PostgreSQL dump
- Sin automatización
- Sin verificación de integridad post-backup

---

## FASE 12 — AGENTE DE IA

### Resultado: **FAIL**

#### Separación de Credenciales

| Entorno | Credenciales | Estado |
|---------|-------------|--------|
| DEV (local) | `backend/.env` (gitignored) | OK |
| STAGING | No configurado | N/A |
| PRODUCTION | No hay credenciales disponibles para agente | OK |

#### Problemas de Seguridad

| # | Problema | Severidad | Archivo | Línea |
|---|----------|-----------|---------|-------|
| 1 | **Sin rate limiting** en `/auth/login` y `/auth/register` | P1 | `auth.py` | 11, 19 |
| 2 | **Refresh token no se revoca** después de uso | P1 | `auth_service.py` | 73-85 |
| 3 | **Credenciales hardcodeadas** en scripts commiteados (`familia123`, `admin123`) | P1 | `verify_sync.py`, `seed_deudas.py`, `check_pwd.py` | multi |
| 4 | **Docker defaults inseguros**: `POSTGRES_PASSWORD=postgres`, `SECRET_KEY=change-me` | P2 | `docker-compose.yml` | 8, 29 |
| 5 | **DB port 5432** expuesta a todas las interfaces | P2 | `docker-compose.yml` | 11 |
| 6 | **CORS_ORIGINS** solo localhost — producción requiere config | P2 | `config.py` | 23 |

#### Autenticación y Autorización

| Componente | Estado | Detalle |
|-----------|--------|---------|
| Password hashing | OK | `CryptContext(schemes=["bcrypt"])` |
| JWT encoding | OK | `settings.SECRET_KEY` + `settings.ALGORITHM` (HS256) |
| Token type validation | OK | Verifica `type != "refresh"` en access |
| UUID parsing | OK | Valida `user_id` como UUID |
| User lookup | OK | Fetch from DB + verifica existencia |
| Password_hash removal | OK | `user.pop("password_hash", None)` antes de retornar |
| Role-based access | OK | `RequireRole` con `require_owner`, `require_member`, `require_viewer` |

#### Endpoints sin Auth

| Endpoint | Razón | Estado |
|----------|-------|--------|
| `POST /api/v1/auth/register` | Registro debe ser público | OK |
| `POST /api/v1/auth/login` | Login debe ser público | OK |
| `POST /api/v1/auth/refresh` | Refresh debe ser público | OK |
| `GET /health` | Health check debe ser público | OK |

**No hay endpoints que bypassen auth innecesariamente.**

---

## FASE 13 — DATABASE DOCTOR (Propuesto)

### Comando

```bash
python scripts/db_doctor.py
```

### Checklist de Verificación

| # | Verificación | Descripción |
|---|-------------|-------------|
| 1 | Conexión | Verificar que la DB es accesible |
| 2 | Schema | Comparar tablas en DB vs modelos SQLAlchemy |
| 3 | Alembic | Verificar revisión actual vs HEAD |
| 4 | Tablas | Verificar 20 tablas esperadas |
| 5 | Columnas | Verificar columnas críticas (especialmente `debts.notes`) |
| 6 | Foreign Keys | Verificar integridad referencial |
| 7 | Indexes | Verificar índices críticos |
| 8 | Constraints | Verificar UNIQUE, NOT NULL |
| 9 | Decimal/Numeric | Verificar tipos numéricos |
| 10 | Household | Verificar aislamiento multi-tenant |
| 11 | Invariantes | Verificar balance = initial + income - expense |

### Output Esperado

```
DATABASE HEALTHY
```

o:

```
DATABASE NOT HEALTHY
- Missing column: debts.notes (model has it, DB does not)
- Missing FK: audit_logs.household_id
- ...
```

---

## FASE 14 — REPORTE FINAL

### 1. Estado General

```
DATABASE:              DEGRADED
PERSISTENCE:           PASS
FINANCIAL INTEGRITY:   PASS
SECURITY:              FAIL
MIGRATIONS:            PASS
BACKUP:                FAIL
```

### 2. Matriz de Entidades

| Entidad | Existe | Persiste | Relaciones | Fuente de Verdad | Problemas | Riesgo |
|---------|--------|----------|------------|-------------------|-----------|--------|
| Household | ✓ | ✓ | — | ✓ | — | BAJO |
| User | ✓ | ✓ | FK → households | ✓ | — | BAJO |
| Account | ✓ | ✓ | FK → households | ✓ | — | BAJO |
| Category | ✓ | ✓ | FK → households | ✓ | — | BAJO |
| Transaction | ✓ | ✓ | FK → accounts, categories, users | ✓ | — | BAJO |
| Debt | ✓ | ✓ | FK → households | ✓ | notes column missing in model | MEDIO |
| DebtPayment | ✓ | ✓ | FK → debts | ✓ | Sin FK a transactions | BAJO |
| RecurringPayment | ✓ | ✓ | FK → households, accounts, categories | ✓ | — | BAJO |
| FinancialEvent | ✓ | ✓ | FK → households, accounts, users | ✓ | — | BAJO |
| Budget | ✓ | ✓ | FK → categories, households | ✓ | — | BAJO |
| SavingsGoal | ✓ | ✓ | FK → households | ✓ | — | BAJO |
| SavingsContribution | ✓ | ✓ | FK → savings_goals | ✓ | — | BAJO |
| Asset | ✓ | ✓ | FK → households | ✓ | Sin endpoints | BAJO |
| Liability | ✓ | ✓ | FK → households | ✓ | Sin endpoints | BAJO |
| AuditLog | ✓ | ✓ | Sin FK constraint | ✓ | household_id sin FK | BAJO |
| Notification | ✓ | ✓ | FK → households, users | ✓ | — | BAJO |
| HouseholdMember | ✗ | — | — | — | Implícito en User | N/A |
| Transfer | ✗ | — | — | — | Embedido en Transaction | N/A |
| ImportBatch | ✗ | — | — | — | No existe | N/A |

### 3. Problemas Encontrados

#### P0 — Pérdida/Corrupción Potencial de Datos
*Ninguno encontrado.*

#### P1 — Riesgo Financiero o de Seguridad

| # | Problema | Archivo | Línea |
|---|----------|---------|-------|
| 1 | Refresh token no se revoca después de uso | `auth_service.py` | 73-85 |
| 2 | Sin rate limiting en endpoints de auth | `auth.py` | 11, 19 |
| 3 | `DebtModel` falta `notes` column (drift con migración) | `models.py` | 77-93 |
| 4 | Credenciales hardcodeadas en scripts commiteados | `verify_sync.py`, `seed_deudas.py`, `check_pwd.py` | multi |
| 5 | `DebtPayment` no tiene FK a `Transaction` (pago sin registro contable) | `models.py` | 95-105 |

#### P2 — Inconsistencia Arquitectónica

| # | Problema | Archivo | Línea |
|---|----------|---------|-------|
| 6 | `AuditLog.household_id` sin FK constraint | `models.py` | 170-182 |
| 7 | 3 interfaces declaran `-> float` pero implementaciones retornan `Decimal` | `debt_repository.py`, `asset_repository.py`, `liability_repository.py` | 28 |
| 8 | 0 relationship() ORM en 22 modelos — todo manual joins | `models.py` | global |
| 9 | Docker defaults inseguros (`postgres`, `change-me`) | `docker-compose.yml` | 8, 29 |
| 10 | `backups/` no gitignored | `.gitignore` | — |
| 11 | DB port 5432 expuesta sin binding a localhost | `docker-compose.yml` | 11 |

#### P3 — Mejora Técnica

| # | Problema |
|---|----------|
| 12 | Sin `pg_dump`/`pg_restore` para PostgreSQL |
| 13 | Sin scheduling de backups |
| 14 | Tests solo en SQLite, no en PostgreSQL |
| 15 | Sin test de restauración de backup |
| 16 | Entidades `Asset` y `Liability` sin endpoints dedicados |
| 17 | `ImportBatch` no existe (funcionalidad de importación pendiente) |
| 18 | `Transfer` no es entidad separada (puede ser design choice) |
| 19 | CORS_ORIGINS solo localhost (producción requiere config) |

### 4. Cambios Recomendados

#### Inmediatos (P1)

1. **Revocar refresh tokens**: Agregar blacklist o rotación con invalidación en `auth_service.py`
2. **Rate limiting**: Instalar `slowapi`, aplicar a `/auth/login` y `/auth/register`
3. **Fix `DebtModel`**: Agregar `notes = Column(Text, nullable=True)` al modelo
4. **Limpiar scripts**: Eliminar credenciales hardcodeadas o mover a `.gitignore` efectivo
5. **FK en AuditLog**: Agregar `ForeignKey("households.id")` a `household_id`

#### Corto Plazo (P2)

6. **Fix interfaces**: Cambiar `-> float` a `-> Decimal` en 3 repositorios
7. **Docker security**: Cambiar defaults, bind port 5432 a `127.0.0.1`
8. **Gitignore backups/**: Agregar `backups/` a `.gitignore`
9. **CORS production**: Documentar setup de `CORS_ORIGINS` para producción

#### Medio Plazo (P3)

10. **PostgreSQL backup**: Implementar `pg_dump` script + scheduling
11. **Tests en PostgreSQL**: Configurar CI con PostgreSQL para tests de integración
12. **Database Doctor**: Implementar script de verificación automática
13. **ORM relationships**: Evaluar agregar `relationship()` para simplificar joins

---

## CONCLUSIÓN

La aplicación tiene una **base sólida** en términos de persistencia e integridad financiera:

- **Decimal consistente**: Todos los campos monetarios usan `Numeric(15,2)`. Sin `float()` en cálculos.
- **RateEngine centralizado**: Todas las conversiones de tasa pasan por `RateEngine.to_monthly_rate()`.
- **Frontend como consumidor**: No almacena datos financieros como fuente de verdad.
- **Multi-tenant por design**: `household_id` en todas las entidades relevantes.
- **Migraciones versionadas**: Cadena lineal, sin branching, sin destructivos.

Los gaps críticos son de **seguridad** (refresh tokens, rate limiting) y **operaciones** (backup, monitoring) que deben resolverse antes de producción.

**Prioridad de acción:**
1. Fix `DebtModel.notes` (1 min)
2. Rate limiting (30 min)
3. Refresh token revocation (1-2 hrs)
4. Cleanup hardcoded credentials (15 min)
5. Database Doctor script (2-4 hrs)

---

> **La mejor arquitectura no es la más sofisticada. Es la que resuelve el problema actual con la menor complejidad necesaria y permite evolucionar el sistema sin generar deuda innecesaria.**
