# Plan de Migración: Excel → Family Financial OS

> **Fecha:** 2026-09-18
> **Estado:** Pendiente de aprobación
> **Fuente:** `Documents/DEUDAS PROYECCION 2026.xlsx` (11 hojas)
> **Destino:** `family_financial.db` (SQLite, DEV)

---

## Resumen Ejecutivo

| Concepto | Valor |
|----------|-------|
| **Estrategia** | Limpieza selectiva + reseed con datos reales del Excel |
| **Deudas a importar** | 12 (Yuleidys excluido, Celular Claro incluido) |
| **Cuentas** | 1 nueva ($2.375.000) |
| **Pagos recurrentes** | 9 (8 expense + 1 income) |
| **Categorías** | 20 (14 existentes + 6 nuevas) |
| **Total entidades** | ~42 registros |
| **Datos conservados** | User, Household, Categories existentes |

---

## FASE 0: Inventario de datos del Excel

### 0.1 — Estructura del Excel

| # | Hoja | Dimensión | Datos reales | Propósito |
|---|------|-----------|-------------|-----------|
| 1 | PROYECCION PAGOS | A1:S991 | ~18 filas | Escenario base de flujo de caja |
| 2 | PROYECCION PAGOS Bancoya | A1:AN991 | ~18 filas | Escenario "Bancoya" |
| 3 | PROYECCION PAGOS Banco Despues | A1:AP991 | ~18 filas | Escenario "Después" |
| 4 | PROYECCION PAGOS renuncia | A1:AN992 | ~18 filas | Escenario "Renuncia" |
| 5 | DISPONIBLE | A1:D1004 | Vacía | Template sin datos |
| 6 | CREDITOS CONTROL | A1:H14 | 13 deudas | Resumen consolidado |
| 7 | CLARO | A1:E26 | 24 cuotas | Amortización celular |
| 8 | BRILLA | A1:H27 | 36 cuotas | Amortización crédito |
| 9 | DAVIVIENDA | A1:G62 | 60 cuotas | Amortización libre inversión |
| 10 | ICETEX | A1:G30 | 24 cuotas | Amortización educativo |
| 11 | RECORDAR | A1:D13 | 12 registros | Plan excequial |

### 0.2 — Deudas a importar (12 registros → `Debt`)

| # | Nombre | Tipo FFO | Total | Saldo actual | Cuota mensual | RateType | Due day | Inicio | Fin |
|---|--------|----------|-------|-------------|---------------|----------|---------|--------|-----|
| 1 | CREDITO | Préstamo personal | $240.000 | $240.000 | — | EA | 30 | — | 30/08/2026 |
| 2 | RAYO | Préstamo personal | $540.000 | $270.000 | $270.000 | EA | 30 | — | 30/08/2026 |
| 3 | RAPICREDIT | Crédito consumo | $355.000 | $355.000 | $130.000 | EA | 15 | — | 15/09/2026 |
| 4 | TIO JOSE | Préstamo personal | $1.000.000 | $1.000.000 | — | EA | 30 | — | 30/10/2026 |
| 5 | MARYI | Préstamo personal | $2.000.000 | $1.800.000 | — | EA | 30 | — | 30/11/2026 |
| 6 | BRILLA | Crédito consumo | $4.200.000 | $4.200.000 | — | EA | 30 | — | 30/01/2027 |
| 7 | ICETEX | Deuda estudiantil | $5.000.000 | $5.000.000 | $300.000 | EA | 30 | — | 30/01/2027 |
| 8 | SIOMARA 1 PRESTAMO | Préstamo personal | $1.530.000 | $1.530.000 | — | EA | 15 | — | 15/02/2027 |
| 9 | JENI PRESTAMO | Préstamo personal | $3.000.000 | $3.000.000 | — | EA | 28 | — | 28/02/2027 |
| 10 | ANDRES DIAN | Préstamo personal | $2.297.000 | $2.297.000 | — | EA | 1 | — | — |
| 11 | DAVIVIENDA | Crédito libre inversión | $38.862.000 | $38.862.000 | $762.000 | EA | 1 | 01/10/2025 | 30/12/2027 |
| 12 | CUOTAS CELULAR CLARO | Dispositivo a crédito | $3.408.000 | $3.408.000 | $142.000 | EA | — | Nov 2025 | Oct 2027 |

**Subtotales por tipo:**
- Préstamos personales: 6 deudas → $8.867.000
- Crédito consumo: 2 deudas → $4.555.000
- Deuda estudiantil: 1 deuda → $5.000.000
- Crédito libre inversión: 1 deuda → $38.862.000
- Dispositivo a crédito: 1 deuda → $3.408.000
- **TOTAL: $60.326.000**

### 0.3 — Cuenta (1 registro → `Account`)

| Nombre | Tipo | Balance | Moneda |
|--------|------|---------|--------|
| Cuenta Principal | bank | $2.375.000 | COP |

*Balance = salario base ($875.000) + ingreso fijo ($1.500.000)*

### 0.4 — Pagos recurrentes (9 registros → `RecurringPayment`)

| # | Nombre | Valor | Tipo | Frecuencia | Día | Categoría |
|---|--------|-------|------|------------|-----|-----------|
| 1 | Salario | $2.375.000 | income | monthly | 1 | Salario |
| 2 | Internet Tigo Casa | $90.000 | expense | monthly | 30 | Servicios |
| 3 | Claro 15 Oscar | $40.000 | expense | monthly | 15 | Servicios |
| 4 | Cuota ICETEX | $300.000 | expense | monthly | 30 | Deuda estudiantil |
| 5 | Cuota Davivienda | $762.000 | expense | monthly | 1 | Crédito libre inversión |
| 6 | Arriendo | $400.000 | expense | monthly | 1 | Vivienda |
| 7 | Mercado | $250.000 | expense | biweekly | 1 | Alimentos |
| 8 | Tarjeta Papi | $40.000 | expense | monthly | 15 | Otros |
| 9 | Plan Excequial | $45.000 | expense | monthly | 1 | Otros |

### 0.5 — Categorías (20 total)

**14 existentes (se conservan):**
Salario, Freelance, Inversiones, Comida, Casa, Transporte, Servicios, Salud, Educación, Gustos, Compras, Deudas, Familia, Otros

**6 nuevas (agregar):**
Cuotas, Vivienda, Alimentos, Plan excequial, Crédito libre inversión, Dispositivo a crédito

### 0.6 — Datos que NO se importan

| Dato | Razón |
|------|-------|
| Yuleidys | Saldo $0, sin aporte financiero |
| 4 hojas de proyección | Son what-if scenarios, ya cubierto en plataforma |
| SARA | Persona que ya no trabaja con la familia |
| OTROS PAGO | Montos agrupados sin desglose individual |
| DISPONIBLE | Hoja vacía |
| RECORDAR (como deuda) | Es plan excequial, se importa como RecurringPayment |

---

## FASE 1: Backup

```bash
cd backend
python scripts/backup_db.py
```

**Resultado:** Zip en `backend/backups/` con el estado actual de `family_financial.db`.

---

## FASE 2: Limpieza selectiva

Crear `backend/clean_for_migration.py`.

### Objetivo
Eliminar solo datos generados/demo, conservando user, household y categories.

### Orden de DELETE (respetando foreign keys)

```
1. audit_logs           (WHERE household_id = ?)
2. financial_events     (WHERE household_id = ?)
3. financial_obligations(WHERE household_id = ?)
4. notifications        (WHERE household_id = ?)
5. category_account_preferences (WHERE household_id = ?)
6. debt_payment_overrides (via debt_id → debts)
7. debt_payments          (via debt_id → debts)
8. transactions         (WHERE household_id = ?)
9. budgets              (WHERE household_id = ?)
10. recurring_payments   (WHERE household_id = ?)
11. savings_contributions (via goal_id → savings_goals)
12. savings_goals        (WHERE household_id = ?)
13. accounts             (WHERE household_id = ?)
14. debts                (WHERE household_id = ?)
```

### Script

```python
"""
Clean database for migration. Keeps users, households, and categories.
Run: python clean_for_migration.py
"""
import asyncio
import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.database import async_session
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


async def clean():
    async with async_session() as db:
        user_repo = SQLAlchemyUserRepository(db)
        user = await user_repo.get_by_email("admin@familia.com")
        if not user or not user["household_id"]:
            print("No hay datos que limpiar.")
            return

        hid = user["household_id"]
        print(f"Limpiando datos del household: {hid}")

        # 1. Direct household tables
        for table in [
            "audit_logs", "financial_events", "financial_obligations",
            "notifications", "category_account_preferences",
            "transactions", "budgets", "recurring_payments",
            "savings_goals", "accounts",
        ]:
            result = await db.execute(text(f"DELETE FROM {table} WHERE household_id = :hid"), {"hid": hid})
            print(f"  {table}: {result.rowcount} rows deleted")

        # 2. Debt sub-tables (via debt_id)
        for table in ["debt_payment_overrides", "debt_payments"]:
            result = await db.execute(text(
                f"DELETE FROM {table} WHERE debt_id IN (SELECT id FROM debts WHERE household_id = :hid)"
            ), {"hid": hid})
            print(f"  {table}: {result.rowcount} rows deleted")

        # 3. Savings sub-tables (via goal_id)
        result = await db.execute(text(
            "DELETE FROM savings_contributions WHERE goal_id IN (SELECT id FROM savings_goals WHERE household_id = :hid)"
        ), {"hid": hid})
        print(f"  savings_contributions: {result.rowcount} rows deleted")

        # 4. Debts (last, after sub-tables)
        result = await db.execute(text("DELETE FROM debts WHERE household_id = :hid"), {"hid": hid})
        print(f"  debts: {result.rowcount} rows deleted")

        await db.commit()
        print("\nLimpieza completada. Conservando: users, households, categories.")


if __name__ == "__main__":
    asyncio.run(clean())
```

---

## FASE 3: Actualizar `seed_deudas.py`

### 3.1 — Corregir montos

```python
# RAPICREDIT (línea ~132-143)
# ANTES:
"current_balance": 225000,
# DESPUÉS:
"current_balance": 355000,

# SIOMARA 1 PRESTAMO (línea ~196-208)
# ANTES:
"total_amount": 1330000,
"current_balance": 1330000,
# DESPUÉS:
"total_amount": 1530000,
"current_balance": 1530000,
```

### 3.2 — Eliminar Yuleidys

Eliminar el diccionario de Yuleidys del array `debts[]` (líneas ~91-104).

### 3.3 — Agregar categorías faltantes

En `default_categories` (líneas ~55-69), agregar:

```python
{"name": "Cuotas", "type": "expense", "icon": "📱", "color": "#f59e0b"},
{"name": "Vivienda", "type": "expense", "icon": "🏘️", "color": "#78716c"},
{"name": "Alimentos", "type": "expense", "icon": "🛒", "color": "#84cc16"},
{"name": "Plan excequial", "type": "expense", "icon": "🕊️", "color": "#6b7280"},
{"name": "Crédito libre inversión", "type": "expense", "icon": "🏦", "color": "#0ea5e9"},
{"name": "Dispositivo a crédito", "type": "expense", "icon": "📱", "color": "#f97316"},
```

### 3.4 — Agregar deuda Celular CLARO

Al final del array `debts[]`:

```python
{
    "name": "Cuotas Celular CLARO",
    "creditor": "Claro",
    "total_amount": 3408000,
    "current_balance": 3408000,
    "interest_rate": 0,
    "interest_rate_type": "EA",
    "minimum_payment": 142000,
    "due_day": 15,
    "start_date": date(2025, 11, 15),
    "end_date": date(2027, 10, 15),
    "status": "active",
},
```

---

## FASE 4: Actualizar `seed_data.py`

### 4.1 — Eliminar secciones demo

Eliminar:
- Transacciones demo (líneas ~58-76)
- Metas de ahorro demo (líneas ~78-90)
- Presupuestos demo (líneas ~108-125)

### 4.2 — Reemplazar cuentas

```python
# ANTES (3 cuentas demo):
accounts_data = [
    {"name": "Banco Principal", "type": "bank", "balance": 1500000, ...},
    {"name": "Efectivo", "type": "cash", "balance": 200000, ...},
    {"name": "Nequi", "type": "ewallet", "balance": 350000, ...},
]

# DESPUÉS (1 cuenta real):
accounts_data = [
    {"name": "Cuenta Principal", "type": "bank", "balance": 2375000, "currency": "COP", "is_active": True},
]
```

### 4.3 — Reemplazar pagos recurrentes

```python
# DESPUÉS (9 recurrents reales):
rec_data = [
    # Income
    {"name": "Salario", "amount": 2375000, "type": "income", "frequency": "monthly",
     "day_of_month": 1, "category_id": cat_map.get("Salario"),
     "next_due_date": date(2026, 10, 1), "is_active": True},

    # Expenses
    {"name": "Internet Tigo Casa", "amount": 90000, "type": "expense", "frequency": "monthly",
     "day_of_month": 30, "category_id": cat_map.get("Servicios"),
     "next_due_date": date(2026, 9, 30), "is_active": True},

    {"name": "Claro 15 Oscar", "amount": 40000, "type": "expense", "frequency": "monthly",
     "day_of_month": 15, "category_id": cat_map.get("Servicios"),
     "next_due_date": date(2026, 10, 15), "is_active": True},

    {"name": "Cuota ICETEX", "amount": 300000, "type": "expense", "frequency": "monthly",
     "day_of_month": 30, "category_id": cat_map.get("Deuda estudiantil"),
     "next_due_date": date(2026, 9, 30), "is_active": True},

    {"name": "Cuota Davivienda", "amount": 762000, "type": "expense", "frequency": "monthly",
     "day_of_month": 1, "category_id": cat_map.get("Crédito libre inversión"),
     "next_due_date": date(2026, 10, 1), "is_active": True},

    {"name": "Arriendo", "amount": 400000, "type": "expense", "frequency": "monthly",
     "day_of_month": 1, "category_id": cat_map.get("Vivienda"),
     "next_due_date": date(2026, 10, 1), "is_active": True},

    {"name": "Mercado", "amount": 250000, "type": "expense", "frequency": "biweekly",
     "day_of_month": 1, "category_id": cat_map.get("Alimentos"),
     "next_due_date": date(2026, 9, 30), "is_active": True},

    {"name": "Tarjeta Papi", "amount": 40000, "type": "expense", "frequency": "monthly",
     "day_of_month": 15, "category_id": cat_map.get("Otros"),
     "next_due_date": date(2026, 10, 15), "is_active": True},

    {"name": "Plan Excequial", "amount": 45000, "type": "expense", "frequency": "monthly",
     "day_of_month": 1, "category_id": cat_map.get("Plan excequial"),
     "next_due_date": date(2026, 10, 1), "is_active": True},
]
```

---

## FASE 5: Ejecución

```bash
cd backend

# 1. Backup
python scripts/backup_db.py

# 2. Limpiar datos viejos
python clean_for_migration.py

# 3. Re-seed deudas (idempotente)
python -m seed_deudas

# 4. Re-seed datos (cuentas + recurring)
python -m seed_data
```

---

## FASE 6: Validación

### 6.1 — Validación automática

```bash
python -c "
import sqlite3
conn = sqlite3.connect('../family_financial.db')
c = conn.cursor()

debts = c.execute('SELECT COUNT(*) FROM debts').fetchone()[0]
total = c.execute('SELECT COALESCE(SUM(current_balance), 0) FROM debts').fetchone()[0]
accounts = c.execute('SELECT COUNT(*) FROM accounts').fetchone()[0]
recurring = c.execute('SELECT COUNT(*) FROM recurring_payments').fetchone()[0]
categories = c.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
events = c.execute('SELECT COUNT(*) FROM financial_events').fetchone()[0]

print('=== INVARIANTES DE MIGRACIÓN ===')
print(f'Deudas:        {debts:>3} (esperado: 12)  {\"✅\" if debts==12 else \"❌\"}')
print(f'Saldo total:   {total:>12,.0f} (esperado: 60,326,000) {\"✅\" if total==60326000 else \"❌\"}')
print(f'Cuentas:       {accounts:>3} (esperado: 1)  {\"✅\" if accounts==1 else \"❌\"}')
print(f'Recurring:     {recurring:>3} (esperado: 9)  {\"✅\" if recurring==9 else \"❌\"}')
print(f'Categorías:    {categories:>3} (esperado: >=20) {\"✅\" if categories>=20 else \"❌\"}')
print(f'Events limpios:{events:>3} (esperado: 0)  {\"✅\" if events==0 else \"❌\"}')

ok = debts==12 and total==60326000 and accounts==1 and recurring==9 and events==0
print(f'\\n{\"✅ MIGRACIÓN APROBADA\" if ok else \"❌ MIGRACIÓN RECHAZADA\"}')"
```

### 6.2 — Validación manual

| # | Verificar | Esperado |
|---|-----------|----------|
| 1 | Abrir app → Deudas | 12 deudas visibles |
| 2 | Yuleidys | NO aparece |
| 3 | Cuotas Celular CLARO | $3.408.000, cuota $142.000 |
| 4 | Davivienda | $38.862.000, tipo "Crédito libre inversión" |
| 5 | ICETEX | $5.000.000, cuota $300.000 |
| 6 | RAPICREDIT | $355.000 |
| 7 | SIOMARA | $1.530.000 |
| 8 | Cuentas → Cuenta Principal | $2.375.000 |
| 9 | Calendario | 9 pagos recurrentes visibles |
| 10 | Salario recurrente | $2.375.000 income |

---

## FASE 7: Invariantes financieras

| # | Invariante | Fórmula SQL | Esperado |
|---|-----------|-------------|----------|
| 1 | Total deudas = Excel | `SELECT SUM(current_balance) FROM debts` | $60.326.000 |
| 2 | Número de deudas | `SELECT COUNT(*) FROM debts` | 12 |
| 3 | Cuenta existe | `SELECT COUNT(*) FROM accounts` | 1 |
| 4 | Balance cuenta | `SELECT balance FROM accounts WHERE name='Cuenta Principal'` | $2.375.000 |
| 5 | Recurring income | `SELECT COUNT(*) FROM recurring_payments WHERE type='income'` | 1 |
| 6 | Recurring expenses | `SELECT COUNT(*) FROM recurring_payments WHERE type='expense'` | 8 |
| 7 | Categorías | `SELECT COUNT(*) FROM categories` | >=20 |
| 8 | Events limpios | `SELECT COUNT(*) FROM financial_events` | 0 |
| 9 | Obligations limpias | `SELECT COUNT(*) FROM financial_obligations` | 0 |

---

## Archivos a modificar/crear

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `backend/clean_for_migration.py` | **Crear** | Script de limpieza selectiva |
| `backend/seed_deudas.py` | **Modificar** | Corregir RAPICREDIT, SIOMARA; eliminar Yuleidys; agregar Celular CLARO; agregar 6 categorías |
| `backend/seed_data.py` | **Modificar** | Eliminar data demo; crear 1 cuenta + 9 recurring payments |
| `Plan-migrationDB.md` | **Crear** | Este documento |

---

## Datos excluidos (justificación)

| Dato | Razón de exclusión |
|------|-------------------|
| Yuleidys | Saldo $0, sin aporte financiero |
| 4 hojas de proyección | Son what-if scenarios, ya cubierto en plataforma |
| SARA | Persona que ya no trabaja con la familia |
| OTROS PAGO | Montos agrupados sin desglose individual |
| DISPONIBLE | Hoja vacía |
| RECORDAR (como deuda) | Es plan excequial, se importa como RecurringPayment |

---

## Post-Migración

Una vez aprobada la migración:
1. El Excel original queda como evidencia en `migration/source/`
2. Los scripts de migración quedan versionados en git
3. Se puede re-ejecutar la migración en cualquier momento
4. La base de datos de referencia para desarrollo queda establish
