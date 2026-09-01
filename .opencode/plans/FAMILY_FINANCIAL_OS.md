# Family Financial OS - Plan de Desarrollo Completo

> **Estado del proyecto**: Planificación inicial  
> **Fase actual**: Fase 0 - Fundamentos (Pendiente)  
> **Última actualización**: Agosto 2026

---

## Índice

1. [Visión del Proyecto](#1-visión-del-proyecto)
2. [Skills Críticas](#2-skills-críticas)
3. [Arquitectura del Sistema](#3-arquitectura-del-sistema)
4. [Financial Engine](#4-financial-engine)
5. [Modelo de Datos](#5-modelo-de-datos)
6. [API REST](#6-api-rest)
7. [Frontend](#7-frontend)
8. [Fases de Desarrollo](#8-fases-de-desarrollo)
9. [Investigación Open Source](#9-investigación-open-source)
10. [QA y Definition of Done](#10-qa-y-definition-of-done)
11. [Privacidad y Seguridad](#11-privacidad-y-seguridad)
12. [Comandos Útiles](#12-comandos-útiles)

---

## 1. Visión del Proyecto

### 1.1 Objetivo

Family Financial OS es el **centro de control financiero de una familia**. Convierte:

```
Datos → Información → Contexto → Decisiones
```

### 1.2 Filosofía

- **No juzgar**: Proporcionar contexto, no criticar gastos
- **Precisión financiera**: Nunca usar floating point para dinero
- **Determinismo**: Cálculos verificables y transparentes
- **Privacidad**: Diseñar pensando en privacidad desde el inicio

### 1.3 Módulos Principales

| Módulo | Función |
|--------|---------|
| **Dinero** | Ingresos, gastos, transferencias, cuentas, tarjetas |
| **Presupuesto** | Planificación consciente por categoría |
| **Deudas** | Registro, pagos, saldos, proyecciones |
| **Ahorro** | Metas, aportes, progreso, cumplimiento |
| **Patrimonio** | Activos, pasivos, patrimonio neto |
| **Proyecciones** | Flujo de caja, escenarios futuros |
| **Familia** | Multi-usuario, roles, compartición |

---

## 2. Skills Críticas

### 2.1 Skills a Instalar (8 skills)

| # | Skill | Fuente | Comando | Uso Principal |
|---|-------|--------|---------|---------------|
| 1 | **xlsx** | NousResearch/hermes-agent | `npx skills add https://github.com/NousResearch/hermes-agent --skill xlsx` | Manejo de Excel fuente |
| 2 | **database-migrations** | affaan-m/ECC | `npx skills add https://github.com/affaan-m/ECC --skill database-migrations` | Migraciones PostgreSQL |
| 3 | **postgres-patterns** | affaan-m/ECC | `npx skills add https://github.com/affaan-m/ECC --skill postgres-patterns` | Diseño DB optimizado |
| 4 | **vue-patterns** | affaan-m/ECC | `npx skills add https://github.com/affaan-m/ECC --skill vue-patterns` | Componentes Vue.js 3 |
| 5 | **python-testing** | affaan-m/ECC | `npx skills add https://github.com/affaan-m/ECC --skill python-testing` | Tests con pytest |
| 6 | **security-review** | affaan-m/ECC | `npx skills add https://github.com/affaan-m/ECC --skill security-review` | Seguridad de datos |
| 7 | **docker-patterns** | affaan-m/ECC | `npx skills add https://github.com/affaan-m/ECC --skill docker-patterns` | Containerización |
| 8 | **deployment-patterns** | affaan-m/ECC | `npx skills add https://github.com/affaan-m/ECC --skill deployment-patterns` | CI/CD y despliegue |

### 2.2 Skills Ya Existentes (No instalar)

| Skill | Uso |
|-------|-----|
| `excel-table-agent` | Lectura del Excel original |
| `firecrawl-*` | Web scraping y research |
| `git-github-workflow-assistant` | Control de versiones |
| `pdf-extractor` | Extracción de PDFs |

### 2.3 Detalle de Skills Críticas

#### xlsx (NousResearch/hermes-agent)
```bash
# Leer Excel fuente
python scripts/xlsx_read.py "DEUDAS PROYECCION 2026.xlsx" --sheets
python scripts/xlsx_read.py "DEUDAS PROYECCION 2026.xlsx" --json --sheet "PROYECCION PAGOS"

# Convertir a CSV
python scripts/xlsx_to_csv.py "DEUDAS PROYECCION 2026.xlsx" output.csv
```

#### postgres-patterns (affaan-m/ECC)
- Query optimization
- Schema design
- Indexing strategies
- RLS (Row Level Security)
- Anti-pattern detection

#### vue-patterns (affaan-m/ECC)
- Composition API patterns
- Component architecture
- Pinia state management
- Vue Router navigation

#### python-testing (affaan-m/ECC)
- pytest fixtures
- Parametrization
- Mocking strategies
- Coverage requirements
- TDD methodology

#### security-review (affaan-m/ECC)
- Authentication patterns
- Input validation
- CSRF protection
- SQL injection prevention
- Secrets management

### 2.4 Mapeo de Skills por Fase

| Fase | Skills Necesarias |
|------|-------------------|
| **Fase 0: Fundamentos** | `xlsx`, `docker-patterns`, `postgres-patterns` |
| **Fase 1: Dinero** | `postgres-patterns`, `python-testing`, `vue-patterns` |
| **Fase 2: Presupuesto** | `python-testing`, `vue-patterns` |
| **Fase 3: Deudas** | `python-testing`, `vue-patterns` |
| **Fase 4: Ahorro** | `python-testing`, `vue-patterns` |
| **Fase 5: Patrimonio** | `python-testing`, `vue-patterns` |
| **Fase 6: Proyecciones** | `python-testing`, `vue-patterns` |
| **Fase 7: Familia** | `security-review`, `python-testing` |
| **Fase 8: Pulido** | `deployment-patterns`, `security-review` |

---

## 3. Arquitectura del Sistema

### 3.1 Stack Tecnológico

| Capa | Tecnología | Justificación |
|------|------------|---------------|
| **Frontend** | Vue.js 3 + Bootstrap 5 | Ligero, reactivo, fácil de aprender |
| **Backend** | FastAPI (Python) | Alto rendimiento, async, auto-documentación |
| **Base de Datos** | PostgreSQL | ACID, confiable, escalable |
| **Migraciones** | Alembic | Control de versiones de esquema |
| **Estado Frontend** | Pinia | Simple, type-safe |
| **Gráficos** | Chart.js + vue-chartjs | Flexible, bien documentado |

### 3.2 Diagrama de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Vue.js)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Dashboard│ │Transacc.│ │Presup.  │ │Deudas   │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────┴──────────────────────────────────┐
│                       API (FastAPI)                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Auth     │ │Endpoints│ │Middleware│ │Schemas  │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                  FINANCIAL ENGINE (Core)                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │CashFlow │ │Budget   │ │Debt     │ │NetWorth │           │
│  │Engine   │ │Engine   │ │Engine   │ │Engine   │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   DATABASE (PostgreSQL)                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Schema/  │ │Models   │ │Migrac.  │ │Seeds    │           │
│  │Household│ │(SQLAlch.)│ │(Alembic)│ │         │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Estructura del Proyecto

```
family-financial-os/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Settings
│   │   ├── database.py                # Async engine
│   │   ├── domain/                    # Entidades y Value Objects
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   └── exceptions.py
│   │   ├── application/               # Services / Use Cases
│   │   │   ├── interfaces/
│   │   │   ├── services/
│   │   │   └── uow.py
│   │   ├── financial_engine/          # Motor Financiero
│   │   │   ├── cash_flow.py
│   │   │   ├── budget_engine.py
│   │   │   ├── debt_engine.py
│   │   │   ├── savings_engine.py
│   │   │   ├── net_worth_engine.py
│   │   │   └── money_operations.py
│   │   ├── infrastructure/            # Implementaciones
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   └── presentation/              # API Routes
│   │       ├── v1/
│   │       └── schemas/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/
│   │   ├── views/
│   │   ├── components/
│   │   ├── composables/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   └── research/
├── docker-compose.yml
└── README.md
```

---

## 4. Financial Engine

### 4.1 Principios

- Independiente del frontend y la API
- Cálculos determinísticos y verificables
- Usa `decimal.Decimal` para todo cálculo monetario
- Sin dependencias de frameworks

### 4.2 Money Value Object

```python
from decimal import Decimal, ROUND_HALF_UP

class Money:
    """Value Object para dinero en COP"""
    
    def __init__(self, amount: Decimal, currency: str = "COP"):
        self.amount = amount.quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )
        self.currency = currency
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise CurrencyMismatchError()
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise CurrencyMismatchError()
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, factor: Decimal) -> 'Money':
        return Money(self.amount * factor, self.currency)
    
    def __gt__(self, other: 'Money') -> bool:
        return self.amount > other.amount
```

### 4.3 Componentes del Engine

| Motor | Funciones |
|-------|-----------|
| **CashFlowEngine** | `calculate_net_income()`, `calculate_cash_flow()`, `project_cash_flow()` |
| **BudgetEngine** | `calculate_budget_status()`, `calculate_category_spending()`, `detect_overruns()` |
| **DebtEngine** | `calculate_balance()`, `calculate_amortization()`, `project_payoff()` |
| **SavingsEngine** | `calculate_progress()`, `project_completion()`, `calculate_savings_rate()` |
| **NetWorthEngine** | `calculate_net_worth()`, `calculate_assets_total()`, `calculate_liabilities_total()` |
| **ProjectionEngine** | `project_3_months()`, `project_6_months()`, `project_12_months()` |

### 4.4 Contrato del Engine

```python
class FinancialEngine:
    """Interfaz principal del Motor Financiero"""
    
    def __init__(self, household_id: str):
        self.household_id = household_id
    
    def get_cash_flow(self, date_from: date, date_to: date) -> CashFlowResult:
        """Calcula flujo de caja para un período"""
        pass
    
    def get_budget_status(self, month: int, year: int) -> BudgetStatusResult:
        """Estado del presupuesto para un mes"""
        pass
    
    def get_debt_summary(self) -> DebtSummaryResult:
        """Resumen de todas las deudas"""
        pass
    
    def get_net_worth(self) -> NetWorthResult:
        """Patrimonio neto actual"""
        pass
    
    def get_savings_progress(self) -> SavingsProgressResult:
        """Progreso de metas de ahorro"""
        pass
    
    def project_scenario(self, months: int, assumptions: ScenarioAssumptions) -> ProjectionResult:
        """Proyectar escenario futuro"""
        pass
```

---

## 5. Modelo de Datos

### 5.1 Schema por Household

```sql
-- Cada hogar tiene su propio schema
CREATE SCHEMA household_abc123;

-- Usuarios
CREATE TABLE household_abc123.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cuentas
CREATE TABLE household_abc123.accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID REFERENCES households(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- cash, bank, wallet, credit_card
    balance DECIMAL(15,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'COP',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Categorías
CREATE TABLE household_abc123.categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL,  -- income, expense
    icon VARCHAR(50),
    color VARCHAR(7)
);

-- Transacciones
CREATE TABLE household_abc123.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    category_id UUID REFERENCES categories(id),
    user_id UUID REFERENCES users(id),
    type VARCHAR(20) NOT NULL,  -- income, expense, transfer
    amount DECIMAL(15,2) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    to_account_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Presupuestos
CREATE TABLE household_abc123.budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(15,2) NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL
);

-- Deudas
CREATE TABLE household_abc123.debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    creditor VARCHAR(255),
    total_amount DECIMAL(15,2) NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2),
    minimum_payment DECIMAL(15,2),
    due_day INT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active'
);

-- Pagos de deudas
CREATE TABLE household_abc123.debt_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    debt_id UUID REFERENCES debts(id),
    amount DECIMAL(15,2) NOT NULL,
    principal DECIMAL(15,2),
    interest DECIMAL(15,2),
    payment_date DATE NOT NULL
);

-- Metas de ahorro
CREATE TABLE household_abc123.savings_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    target_amount DECIMAL(15,2) NOT NULL,
    current_amount DECIMAL(15,2) DEFAULT 0,
    target_date DATE,
    priority VARCHAR(20) DEFAULT 'medium'
);

-- Aportes de ahorro
CREATE TABLE household_abc123.savings_contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID REFERENCES savings_goals(id),
    amount DECIMAL(15,2) NOT NULL,
    contribution_date DATE NOT NULL
);

-- Activos
CREATE TABLE household_abc123.assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    value DECIMAL(15,2) NOT NULL,
    purchase_date DATE
);

-- Pasivos
CREATE TABLE household_abc123.liabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2),
    monthly_payment DECIMAL(15,2)
);
```

### 5.2 Diagrama ER

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Households │────<│    Users    │     │  Categories │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                        │
       ├────────────────────────────────────────┤
       │                                        │
       ▼                                        ▼
┌─────────────┐                         ┌─────────────┐
│   Accounts  │────<│ Transactions │>────│  Budgets    │
└─────────────┘                         └─────────────┘
       │
       ├────────────────────────────────────────┐
       │                                        │
       ▼                                        ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Debts    │────<│DebtPayments │     │SavingsGoals │
└─────────────┘     └─────────────┘     └─────────────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │Contributions│
                                         └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Assets    │     │Liabilities  │
└─────────────┘     └─────────────┘
```

---

## 6. API REST

### 6.1 Endpoints Principales

| Módulo | Endpoints | Descripción |
|--------|-----------|-------------|
| **Auth** | POST `/auth/register`, `/auth/login`, `/auth/refresh`, GET `/auth/me` | Autenticación JWT |
| **Household** | CRUD + `/invite` | Gestión de hogar |
| **Accounts** | CRUD + `/{id}/balance` | Cuentas bancarias |
| **Transactions** | CRUD + `/transfer` | Transacciones |
| **Budgets** | CRUD + `/status/{month}/{year}` | Presupuestos |
| **Debts** | CRUD + `/payments`, `/amortization`, `/projection` | Deudas |
| **Savings** | CRUD + `/contributions`, `/projection` | Metas ahorro |
| **Assets** | CRUD | Activos |
| **Liabilities** | CRUD | Pasivos |
| **Dashboard** | GET `/dashboard`, `/cash-flow`, `/net-worth` | Resumen |
| **Projections** | GET + POST `/scenario` | Proyecciones |

### 6.2 Autenticación

```python
# JWT Authentication
# - Access token: 30 minutos
# - Refresh token: 7 días
# - Roles: owner, member, viewer
```

### 6.3 Respuestas Estándar

```json
{
    "success": true,
    "data": { ... },
    "meta": { "page": 1, "per_page": 20, "total": 100 }
}
```

---

## 7. Frontend

### 7.1 Stack

- **Framework**: Vue.js 3 (Composition API)
- **UI**: Bootstrap 5
- **State**: Pinia
- **Router**: Vue Router 4
- **HTTP**: Axios
- **Charts**: Chart.js + vue-chartjs
- **Forms**: VeeValidate + Yup
- **Date**: date-fns
- **Build**: Vite

### 7.2 Vistas

| Vista | Descripción |
|-------|-------------|
| Dashboard | Resumen: saldo, ingresos, gastos, ahorro |
| Accounts | Gestión de cuentas |
| Transactions | Registro y historial |
| Budget | Presupuesto consciente vs gasto real |
| Debts | Control de deudas con amortización |
| Savings | Metas y progreso |
| Assets | Activos y patrimonio |
| Projections | Simuladores y proyecciones |
| Household | Gestión de miembros |

### 7.3 Presupuesto Consciente

```
Categoría      │ Presupuesto │ Gasto    │ Saldo   │ Estado
───────────────┼─────────────┼──────────┼─────────┼────────
Alimentación   │ $800.000    │ $620.000 │ $180.000│ ✅
Transporte     │ $300.000    │ $250.000 │ $50.000 │ ✅
Entretenimiento│ $150.000    │ $170.000 │-$20.000 │ ⚠️

💡 "Entretenimiento excedió $20.000 (13.3%). 
    Considere revisar el presupuesto."
```

---

## 8. Fases de Desarrollo

### Fase 0: Fundamentos (Semana 1-2)

| Tarea | Estado |
|-------|--------|
| Configurar proyecto backend (FastAPI + PostgreSQL) | [ ] |
| Configurar proyecto frontend (Vue.js + Bootstrap) | [ ] |
| Implementar Money Value Object | [ ] |
| Configurar autenticación JWT | [ ] |
| Crear schema base de datos | [ ] |
| Configurar Alembic para migraciones | [ ] |
| Configurar Docker Compose | [ ] |
| Instalar skills críticas | [ ] |

---

### Fase 1: Dinero (Semana 3-4)

| Tarea | Estado |
|-------|--------|
| CRUD de cuentas | [ ] |
| CRUD de categorías | [ ] |
| CRUD de transacciones | [ ] |
| Transferencias entre cuentas | [ ] |
| Dashboard con saldo total | [ ] |
| Vista de transacciones con filtros | [ ] |

---

### Fase 2: Presupuesto Consciente (Semana 5-6)

| Tarea | Estado |
|-------|--------|
| CRUD de presupuestos por categoría | [ ] |
| Comparación presupuesto vs gasto real | [ ] |
| Cálculo de saldo restante | [ ] |
| Detección de excedentes | [ ] |
| Indicadores visuales (✅/⚠️/❌) | [ ] |
| Contexto explicativo | [ ] |
| Gráfico de barras comparativo | [ ] |

---

### Fase 3: Deudas (Semana 7-8)

| Tarea | Estado |
|-------|--------|
| CRUD de deudas | [ ] |
| Registro de pagos | [ ] |
| Cálculo de saldos | [ ] |
| Tabla de amortización | [ ] |
| Proyección de fecha de pago final | [ ] |
| Alertas de vencimiento | [ ] |

---

### Fase 4: Ahorro (Semana 9)

| Tarea | Estado |
|-------|--------|
| CRUD de metas de ahorro | [ ] |
| Registro de aportes | [ ] |
| Cálculo de progreso | [ ] |
| Proyección de cumplimiento | [ ] |
| Tasa de ahorro | [ ] |

---

### Fase 5: Patrimonio (Semana 10)

| Tarea | Estado |
|-------|--------|
| CRUD de activos | [ ] |
| CRUD de pasivos | [ ] |
| Cálculo de patrimonio neto | [ ] |
| Gráfico activos vs pasivos | [ ] |

---

### Fase 6: Proyecciones (Semana 11-12)

| Tarea | Estado |
|-------|--------|
| Proyección de flujo de caja | [ ] |
| Proyección de deudas | [ ] |
| Proyección de ahorro | [ ] |
| Simulador de escenarios | [ ] |
| Exportación de reportes | [ ] |

---

### Fase 7: Familia (Semana 13)

| Tarea | Estado |
|-------|--------|
| Sistema de roles (owner, member, viewer) | [ ] |
| Invitación de miembros | [ ] |
| Permisos por rol | [ ] |
| Registro de quién hizo cada operación | [ ] |

---

### Fase 8: Pulido y Lanzamiento (Semana 14)

| Tarea | Estado |
|-------|--------|
| Tests unitarios completos | [ ] |
| Tests de integración | [ ] |
| Validación de inputs | [ ] |
| Manejo de errores | [ ] |
| Documentación de API (Swagger) | [ ] |
| README completo | [ ] |

---

## 9. Investigación Open Source

### 9.1 Proyectos de Referencia

| Proyecto | GitHub | Lección | Clasificación |
|----------|--------|---------|---------------|
| Actual Budget | actualbudget/actual | Envelope budgeting, local-first | INSPIRE |
| Firefly III | firefly-iii/firefly-iii | Double-entry, arquitectura modular | REUSE |
| Wealthfolio | wealthfolio/wealthfolio | Privacidad, patrimonio | INSPIRE |
| FamilyAccountant | aj1126/FamilyAccountant | Offline-first, monorepo | ADAPT |

### 9.2 Research por Módulo

```
docs/research/
├── budgets/
├── debts/
├── projections/
├── offline-first/
└── security/
```

---

## 10. QA y Definition of Done

### 10.1 Definition of Done

- [ ] Requisito definido
- [ ] Investigación realizada
- [ ] Implementación completada
- [ ] Tests escritos y pasando
- [ ] Edge cases manejados
- [ ] Seguridad verificada
- [ ] Documentación actualizada

### 10.2 QA Score por Fase

| Criterio | Puntuación |
|----------|------------|
| Functional | /10 |
| Data Integrity | /10 |
| Security | /10 |
| Testing | /10 |
| UX | /10 |
| Documentation | /10 |

**Una fase es READY solo cuando cumple todos los criterios.**

---

## 11. Privacidad y Seguridad

### 11.1 Principios

1. No almacenar secretos en Git
2. No loggear información financiera sensible
3. Validar todos los inputs
4. Manejar errores de forma segura
5. Backups de base de datos

### 11.2 Roles

| Rol | Permisos |
|-----|----------|
| **Owner** | Gestionar hogar, invitar/eliminar, todos los datos |
| **Member** | Ver datos, crear transacciones, gestionar presupuesto |
| **Viewer** | Solo ver datos y reportes |

---

## 12. Comandos Útiles

### 12.1 Instalación de Skills

```bash
# Instalar skills críticas
npx skills add https://github.com/NousResearch/hermes-agent --skill xlsx
npx skills add https://github.com/affaan-m/ECC --skill database-migrations
npx skills add https://github.com/affaan-m/ECC --skill postgres-patterns
npx skills add https://github.com/affaan-m/ECC --skill vue-patterns
npx skills add https://github.com/affaan-m/ECC --skill python-testing
npx skills add https://github.com/affaan-m/ECC --skill security-review
npx skills add https://github.com/affaan-m/ECC --skill docker-patterns
npx skills add https://github.com/affaan-m/ECC --skill deployment-patterns
```

### 12.2 Backend

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
alembic upgrade head
alembic revision --autogenerate -m "descripcion"
pytest
```

### 12.3 Frontend

```bash
npm install
npm run dev
npm run build
npm run test
npm run lint
```

### 12.4 Base de Datos

```bash
psql -U postgres -d family_financial_os
pg_dump -U postgres family_financial_os > backup.sql
```

---

## 13. Objetivo Final

Construir un sistema que permita a una familia pasar de:

> "No sabemos exactamente dónde se nos va el dinero."

a:

> "Sabemos cuánto tenemos,
> dónde está,
> qué debemos,
> qué podemos gastar,
> qué estamos construyendo
> y hacia dónde vamos."

---

## 14. Referencia Rápida para Nueva Sesión

```bash
# 1. Revisar este plan
cat .opencode/plans/FAMILY_FINANCIAL_OS.md

# 2. Instalar skills (si no están instaladas)
# Ver sección 12.1

# 3. Verificar fase actual
# Buscar "Fase actual" al inicio del documento

# 4. Continuar con la siguiente fase pendiente
```

---

**Fin del Plan**
