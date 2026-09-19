# SCHEMA.md — Schema de Base de Datos

> **Motor:** SQLite (desarrollo) / PostgreSQL 16 (produccion)
> **ORM:** SQLAlchemy 2.0 (async)
> **Migraciones:** Alembic (11 versiones)
> **UUID:** `String(36)` (compatible con SQLite)
> **Moneda:** `Numeric(15, 2)` para todo campo monetario

---

## Diagrama de Relaciones

```
households (1) ──┬── users (N)
                 ├── accounts (N)
                 ├── categories (N)
                 ├── budgets (N)
                 ├── debts (N)
                 │     └── debt_payments (N)
                 │     └── debt_payment_overrides (N)
                 ├── savings_goals (N)
                 │     └── savings_contributions (N)
                 ├── recurring_payments (N)
                 ├── assets (N)
                 ├── liabilities (N)
                 ├── audit_logs (N)
                 ├── notifications (N)
                 ├── financial_obligations (N)
                 ├── financial_events (N)
                 └── category_account_preferences (N)

accounts (1) ──┬── transactions (N, via account_id)
               ├── transactions (N, via to_account_id)
               └── recurring_payments (N)

categories (1) ──┬── transactions (N)
                  ├── budgets (N)
                  ├── recurring_payments (N)
                  ├── financial_obligations (N)
                  ├── financial_events (N)
                  └── category_account_preferences (N)

users (1) ──┬── transactions (N)
            ├── debt_payment_overrides (N, via marked_by)
            ├── notifications (N)
            ├── financial_obligations (N, via responsible_member_id)
            ├── financial_events (N, via responsible_member_id)
            └── financial_events (N, via paid_by)
```

---

## Tablas

### households
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| name | String(255) | NOT NULL | Nombre del hogar |
| created_at | DateTime | default=utcnow | Fecha de creacion |

### users
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| email | String(255) | UNIQUE, NOT NULL | Email del usuario |
| name | String(255) | NOT NULL | Nombre completo |
| password_hash | String(255) | NOT NULL | Hash bcrypt del password |
| role | String(50) | default="member" | Rol: owner, member, viewer |
| household_id | String(36) | FK households.id, nullable | Hogar al que pertenece |
| created_at | DateTime | default=utcnow | Fecha de creacion |

### accounts
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL, INDEX | Hogar propietario |
| name | String(255) | NOT NULL | Nombre de la cuenta |
| type | String(50) | NOT NULL | Tipo: cash, bank, wallet, digital_wallet, credit_card |
| balance | Numeric(15,2) | default=0 | Balance actual en COP |
| currency | String(3) | default="COP" | Codigo ISO de moneda |
| is_active | Boolean | default=True | Si la cuenta esta activa |
| created_at | DateTime | default=utcnow | Fecha de creacion |

### categories
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| name | String(255) | NOT NULL | Nombre de la categoria |
| type | String(20) | NOT NULL | Tipo: income, expense |
| icon | String(50) | nullable | Identificador de icono |
| color | String(7) | nullable | Codigo hex de color |

### transactions
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| account_id | String(36) | FK accounts.id, NOT NULL | Cuenta origen |
| category_id | String(36) | FK categories.id, nullable | Categoria |
| user_id | String(36) | FK users.id, NOT NULL | Usuario que creo |
| type | String(20) | NOT NULL | Tipo: income, expense, transfer |
| amount | Numeric(15,2) | NOT NULL | Monto en COP |
| description | Text | nullable | Descripcion opcional |
| date | Date | NOT NULL | Fecha de la transaccion |
| to_account_id | String(36) | FK accounts.id, nullable | Cuenta destino (transferencias) |
| created_at | DateTime | default=utcnow | Fecha de creacion |

### budgets
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| category_id | String(36) | FK categories.id, NOT NULL | Categoria |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| amount | Numeric(15,2) | NOT NULL | Presupuesto mensual en COP |
| month | Integer | NOT NULL | Mes (1-12) |
| year | Integer | NOT NULL | Ano (2020-2100) |

### debts
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| name | String(255) | NOT NULL | Nombre de la deuda |
| creditor | String(255) | nullable | Acreedor o prestamista |
| total_amount | Numeric(15,2) | NOT NULL | Monto total original |
| current_balance | Numeric(15,2) | NOT NULL | Balance actual pendiente |
| interest_rate | Numeric(5,2) | default=0 | Tasa de interes anual (%) |
| interest_rate_type | String(20) | default="EA" | Tipo de tasa: EA, EM, nominal, daily |
| minimum_payment | Numeric(15,2) | default=0 | Pago minimo mensual |
| due_day | Integer | default=1 | Dia de vencimiento (1-31) |
| start_date | Date | nullable | Fecha de inicio |
| end_date | Date | nullable | Fecha esperada de pago |
| status | String(50) | default="active" | Estado: active, paused, paid |

### debt_payments
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| debt_id | String(36) | FK debts.id, NOT NULL | Deuda asociada |
| amount | Numeric(15,2) | NOT NULL | Monto del pago |
| principal | Numeric(15,2) | nullable | Porcion de capital |
| interest | Numeric(15,2) | nullable | Porcion de interes |
| payment_date | Date | NOT NULL | Fecha del pago |
| is_reversed | Boolean | default=False | Si el pago fue reversado |

### debt_payment_overrides
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| debt_id | String(36) | FK debts.id, NOT NULL | Deuda asociada |
| year | Integer | NOT NULL | Ano |
| month | Integer | NOT NULL | Mes (1-12) |
| is_paid | Boolean | default=True | Si fue pagado |
| marked_by | String(36) | FK users.id, nullable | Quien marco |
| marked_at | DateTime | default=utcnow | Cuando se marco |

### savings_goals
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| name | String(255) | NOT NULL | Nombre de la meta |
| target_amount | Numeric(15,2) | NOT NULL | Monto objetivo |
| current_amount | Numeric(15,2) | default=0 | Monto actual ahorrado |
| target_date | Date | nullable | Fecha objetivo |
| monthly_contribution | Numeric(15,2) | nullable | Aporte mensual |
| priority | String(20) | default="medium" | Prioridad: low, medium, high |
| description | Text | nullable | Descripcion corta |
| goal_type | String(20) | default="savings" | Tipo: savings, investment |
| expected_return_rate | Numeric(5,2) | nullable | Tasa de retorno anual (%) |
| horizon_months | Integer | nullable | Horizonte en meses |

### savings_contributions
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| goal_id | String(36) | FK savings_goals.id, NOT NULL | Meta asociada |
| amount | Numeric(15,2) | NOT NULL | Monto del aporte |
| contribution_date | Date | NOT NULL | Fecha del aporte |

### assets
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| name | String(255) | NOT NULL | Nombre del activo |
| type | String(50) | NOT NULL | Tipo: property, vehicle, investment, other |
| value | Numeric(15,2) | NOT NULL | Valor actual |
| purchase_date | Date | nullable | Fecha de compra |

### liabilities
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| name | String(255) | NOT NULL | Nombre del pasivo |
| type | String(50) | NOT NULL | Tipo |
| total_amount | Numeric(15,2) | NOT NULL | Monto total |
| current_balance | Numeric(15,2) | NOT NULL | Balance actual |
| interest_rate | Numeric(5,2) | default=0 | Tasa de interes |
| interest_rate_type | String(20) | default="EA" | Tipo de tasa |
| monthly_payment | Numeric(15,2) | default=0 | Pago mensual |

### recurring_payments
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| account_id | String(36) | FK accounts.id, nullable | Cuenta asociada |
| category_id | String(36) | FK categories.id, nullable | Categoria |
| name | String(255) | NOT NULL | Nombre del pago |
| amount | Numeric(15,2) | NOT NULL | Monto |
| type | String(20) | NOT NULL, default="expense" | Tipo: expense, income |
| frequency | String(20) | NOT NULL, default="monthly" | Frecuencia: weekly, biweekly, monthly, yearly |
| day_of_month | Integer | default=1 | Dia del mes |
| next_due_date | Date | NOT NULL | Siguiente fecha de vencimiento |
| is_active | Boolean | default=True | Si esta activo |
| description | Text | nullable | Descripcion |
| created_at | DateTime | default=utcnow | Fecha de creacion |

### notifications
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL, INDEX | Hogar propietario |
| user_id | String(36) | FK users.id, NOT NULL, INDEX | Usuario destinatario |
| type | String(50) | NOT NULL | Tipo: alert, reminder, info |
| title | String(255) | NOT NULL | Titulo |
| message | Text | NOT NULL | Mensaje |
| data | Text | nullable | Datos adicionales (JSON) |
| is_read | Boolean | default=False | Si fue leida |
| created_at | DateTime | default=utcnow | Fecha de creacion |

### audit_logs
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | NOT NULL, INDEX | Hogar |
| user_id | String(36) | NOT NULL | Usuario |
| user_email | String(255) | NOT NULL | Email del usuario |
| action | String(50) | NOT NULL | Accion: create, update, delete |
| entity_type | String(50) | NOT NULL | Tipo de entidad |
| entity_id | String(36) | nullable | ID de la entidad |
| entity_name | String(255) | nullable | Nombre de la entidad |
| details | Text | nullable | Detalles adicionales |
| created_at | DateTime | default=utcnow | Fecha de la accion |

### financial_obligations
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL, INDEX | Hogar propietario |
| source | String(20) | NOT NULL | Fuente: USER, DEBT, RECURRING |
| source_id | String(36) | nullable | ID de la entidad fuente |
| name | String(255) | NOT NULL | Nombre |
| type | String(20) | NOT NULL | Tipo: expense, payment, debt, income, goal |
| amount | Numeric(15,2) | NOT NULL | Monto |
| currency | String(3) | default="COP" | Moneda |
| frequency | String(20) | default="monthly" | Frecuencia |
| anchor_day | Integer | nullable | Dia del mes |
| recommended_offset_days | Integer | default=5 | Dias antes para fecha recomendada |
| cutoff_offset_days | Integer | nullable | Dias antes para fecha de corte |
| reminder_days_before | Integer | default=3 | Dias antes para recordatorio |
| account_id | String(36) | FK accounts.id, nullable | Cuenta asociada |
| category_id | String(36) | FK categories.id, nullable | Categoria |
| responsible_member_id | String(36) | FK users.id, nullable | Miembro responsable |
| is_active | Boolean | default=True | Si esta activa |
| confidence | Integer | default=100 | Confianza del sistema (0-100) |
| notes | Text | nullable | Notas |
| created_at | DateTime | default=utcnow | Fecha de creacion |
| updated_at | DateTime | default=utcnow | Ultima actualizacion |

### financial_events
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL, INDEX | Hogar propietario |
| source | String(20) | NOT NULL | Fuente: USER, DEBT, RECURRING, OBLIGATION |
| source_id | String(36) | nullable | ID de la entidad fuente |
| type | String(20) | NOT NULL | Tipo: expense, payment, debt, income, goal |
| title | String(255) | NOT NULL | Titulo |
| amount | Numeric(15,2) | NOT NULL | Monto |
| currency | String(3) | default="COP" | Moneda |
| due_date | Date | NOT NULL | Fecha de vencimiento |
| recommended_date | Date | nullable | Fecha recomendada de pago |
| cutoff_date | Date | nullable | Fecha de corte |
| status | String(20) | default="pending" | Estado: pending, paid |
| account_id | String(36) | FK accounts.id, nullable | Cuenta asociada |
| responsible_member_id | String(36) | FK users.id, nullable | Miembro responsable |
| is_recurrent | Boolean | default=False | Si es recurrente |
| recurrence_group_id | String(36) | nullable | ID del grupo de recurrencia |
| reminder_days_before | Integer | default=3 | Dias antes para recordatorio |
| notes | Text | nullable | Notas |
| confirmed | Boolean | default=True | Si esta confirmado |
| paid_at | DateTime | nullable | Timestamp de pago |
| paid_amount | Numeric(15,2) | nullable | Monto pagado |
| paid_by | String(36) | FK users.id, nullable | Quien pago |
| obligation_id | String(36) | nullable, INDEX | Obligacion asociada |
| category_id | String(36) | FK categories.id, nullable | Categoria |
| visibility | String(12) | default="confirmed" | Visibilidad: confirmed, scheduled, estimated |
| confidence | Integer | default=100 | Confianza (0-100) |
| payment_method | String(12) | nullable | Metodo: card, cash, transfer |
| consequence_note | Text | nullable | Nota de consecuencia |
| created_at | DateTime | default=utcnow | Fecha de creacion |
| updated_at | DateTime | default=utcnow | Ultima actualizacion |

### category_account_preferences
| Columna | Tipo | Constraints | Descripcion |
|---------|------|-------------|-------------|
| id | String(36) | PK, default=uuid4 | Identificador unico |
| household_id | String(36) | FK households.id, NOT NULL | Hogar propietario |
| category_id | String(36) | FK categories.id, NOT NULL | Categoria |
| account_id | String(36) | FK accounts.id, NOT NULL | Cuenta predeterminada |
| created_at | DateTime | default=utcnow | Fecha de creacion |

---

## Indices

| Tabla | Indice | Tipo |
|-------|--------|------|
| accounts | household_id | INDEX |
| debts | household_id | INDEX |
| audit_logs | household_id | INDEX |
| financial_events | household_id | INDEX |
| financial_obligations | household_id | INDEX |
| notifications | household_id | INDEX |
| notifications | user_id | INDEX |
| financial_events | obligation_id | INDEX |

---

## Migraciones Alembic

| # | Version | Descripcion |
|---|---------|-------------|
| 1 | 7b3de54cad72 | Schema inicial (accounts, categories, transactions, budgets, debts, payments, savings, assets, liabilities, audit) |
| 2 | a1b2c3d4e5f6 | Payment reversal + debt payment overrides |
| 3 | b3c4d5e6f7a8 | Monthly contribution en savings_goals |
| 4 | d0431b0b55d0 | Tabla notifications |
| 5 | e5f6a7b8c9d0 | Tabla preferences + extension goals |
| 6 | f1a2b3c4d5e6 | Tabla financial_events |
| 7 | g2h3i4j5k6l7 | Tabla financial_obligations |
| 8 | h3i4j5k6l7m8 | category_id en financial_events |
| 9 | i4j5k6l7m8n9 | interest_rate_type en debts |
| 10 | m1n2o3p4q5r6 | description en savings_goals |
| 11 | 20260904_090300 | Indices de rendimiento en household_id |

---

## Convenciones de Schema

- **UUID:** `String(36)` para compatibilidad con SQLite. En PostgreSQL futuro se puede migrar a UUID nativo.
- **Moneda:** Siempre `Numeric(15,2)`. Nunca `Float`.
- **Fechas:** `Date` para fechas, `DateTime` para timestamps.
- **Strings:** `String(N)` con N especificado. `Text` para contenido largo.
- **Booleans:** `Boolean` con `default=True` o `default=False`.
- **Foreign Keys:** Siempre `String(36)` referenciando a la tabla padre.
- **Nullable:** `nullable=True` para campos opcionales. `nullable=False` para requeridos.
- **Defaults:** `default=uuid4()` para IDs, `default=utcnow` para timestamps.
