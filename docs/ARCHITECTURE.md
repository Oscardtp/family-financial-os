# ARCHITECTURE.md — Arquitectura del Sistema

## Vision General

Family Financial OS sigue **Clean Architecture** con separacion en 5 capas. El backend es una API REST con FastAPI, el frontend es una SPA con Vue.js 3.

```
+-----------------------------------------------------------+
|                   PRESENTATION (HTTP)                      |
|  Routers FastAPI + Schemas Pydantic + DI (deps.py)        |
|  19 routers, ~50 schemas, error_handlers.py               |
+-----------------------------------------------------------+
|                 APPLICATION (Use Cases)                    |
|  Services + Repository Interfaces (Ports)                 |
|  15 services, 18 interfaces                               |
+-----------------------------------------------------------+
|               INFRASTRUCTURE (Persistence)                 |
|  SQLAlchemy Models + Repository Implementations            |
|  19 models, 20 repos                                     |
+-----------------------------------------------------------+
|                    DOMAIN (Core)                           |
|  Value Objects + Entities + Exceptions                    |
|  Money, InterestRate, 14 entities, 3 exceptions           |
+-----------------------------------------------------------+
|              FINANCIAL ENGINE (Computation)                |
|  Pure calculation engines                                 |
|  12 engines: amortization, debt, savings, projections     |
+-----------------------------------------------------------+
```

**Flujo de dependencias:**
```
Presentation -> Application -> Domain <- Infrastructure
                                    ^
                            Financial Engine
```

---

## Backend (`backend/`)

### Estructura

```
backend/
  app/
    domain/                    # Value Objects, Entities, Exceptions
      value_objects/
        money.py               # Money VO: Decimal precision, COP
        interest_rate.py        # InterestRate VO: frozen dataclass
      entities/
        entities.py            # 14 dataclasses (User, Account, Debt, etc.)
      exceptions.py            # CurrencyMismatch, InsufficientFunds, InvalidAmount
    application/               # Business Logic
      interfaces/              # Repository Interfaces (Ports)
        18 interfaces
      services/                # Application Services
        15 services
    infrastructure/            # Persistence
      models/
        models.py              # 19 SQLAlchemy models
      repositories/            # Repository Implementations
        20 repos
    presentation/              # HTTP Layer
      v1/                      # API Routers
        19 routers
      schemas/
        schemas.py             # ~50 Pydantic schemas (672 lineas)
        calendar_schemas.py    # Schemas del calendario
      deps.py                  # JWT, bcrypt, RequireRole DI
      error_handlers.py        # Friendly HTTP messages en espanol
      audit_helper.py          # Helper para logging de auditoria
    financial_engine/          # Pure Calculation Engines
      rate_engine.py           # Conversion de tasas EA/EM/NOMINAL/DAILY
      debt_engine.py           # Resumen y proyeccion de deudas
      amortization.py          # Tablas de amortizacion
      savings_engine.py        # Progreso y proyeccion de metas
      projection_engine.py     # Escenarios y proyecciones
      cash_flow.py             # Flujo de caja historico
      cash_flow_projection.py  # Proyeccion de flujo a futuro
      budget_engine.py         # Estado y proyeccion de presupuestos
      net_worth_engine.py      # Calculo de patrimonio
      calendar_engine.py       # Generacion de eventos recurrentes
      money_operations.py      # Operaciones generales con Money
      helpers.py               # Utilidades (months_between)
    config.py                  # Settings con Path absoluto
    database.py                # Async engine + session factory
    main.py                    # FastAPI app + lifespan (Alembic)
  alembic/                     # 11 migraciones
  tests/                       # 147 tests
  requirements.txt
  Dockerfile
```

### Capas Detalladas

#### Domain (`domain/`)

El nucleo del sistema. Sin dependencias de frameworks.

**Value Objects:**
- `Money`: VO inmutable para dinero. Usa `Decimal` con cuantizacion a 2 decimales. Soporta operaciones aritmeticas (+, -, *, comparaciones). Valida moneda en cada operacion. Factory methods: `Money.zero()`, `Money.from_cents()`.
- `InterestRate`: Frozen dataclass con `value: Decimal` y `rate_type: RateType`. RateType es un Enum: EA, EM, NOMINAL, DAILY.

**Entities:** 14 dataclasses que representan las entidades del dominio. Actualmente son anemicas (sin comportamiento).
- User, Account, Category, Transaction, Budget, Debt, DebtPayment, SavingsGoal, SavingsContribution, RecurringPayment, FinancialObligation, FinancialEvent, Asset, Liability

**Exceptions:**
- `CurrencyMismatchError`: Operacion entre Money con diferentes monedas
- `InsufficientFundsError`: Fondos insuficientes
- `InvalidAmountError`: Monto invalido

#### Application (`application/`)

Contiene la logica de negocio y los puertos (interfaces) para la infraestructura.

**Repository Interfaces (18):**
Cada entidad tiene su interfaz de repositorio con metodos como `get_by_id()`, `get_all()`, `create()`, `update()`, `delete()`. Son abstractas (ABC) y definen el contrato que la infraestructura debe cumplir.

**Services (15):**
- `auth_service.py`: Registro, login, refresh tokens
- `account_service.py`: CRUD de cuentas
- `transaction_service.py`: CRUD de transacciones
- `budget_service.py`: CRUD de presupuestos
- `debt_service.py`: CRUD de deudas, pagos, amortizacion, alertas
- `savings_service.py`: CRUD de metas de ahorro, aportes, proyecciones
- `dashboard_service.py`: Resumen financiero completo (240 lineas, 8 repos)
- `event_service.py`: CRUD de eventos financieros
- `calendar_service.py`: Disponibilidad, preparacion del mes
- `calendar_debt_sync_service.py`: Sincronizacion deuda-calendario
- `obligation_service.py`: CRUD de obligaciones
- `obligation_sync_service.py`: Sincronizacion obligacion-evento
- `recurring_payment_service.py`: CRUD de pagos recurrentes
- `notification_service.py`: CRUD de notificaciones
- `learning_service.py`: Deteccion de patrones

**Nota:** Los services crean repositorios concretos internamente (no usan DI). Esto es un problema de arquitectura conocido.

#### Infrastructure (`infrastructure/`)

Implementacion concreta de los puertos usando SQLAlchemy 2.0 async.

**Models (19):** Modelos SQLAlchemy en `models.py`. Cada modelo mapea a una tabla. Usan `String(36)` para UUIDs, `Numeric(15,2)` para dinero, `DateTime` para timestamps.

**Repositories (20):** Implementaciones concretas de las interfaces. Retornan `dict` en lugar de entidades de dominio. Metodos: `get_by_id()`, `get_all()`, `create()`, `update()`, `delete()` + metodos especificos por entidad.

#### Presentation (`presentation/`)

Capa HTTP con FastAPI.

**Routers (19):** Un router por dominio. Cada endpoint usa `Depends(get_db)` para la sesion y `Depends(require_viewer/member/owner)` para autorizacion.

**Schemas (~50):** Pydantic v2 schemas para request/response. Un solo archivo `schemas.py` de 672 lineas.

**DI (`deps.py`):** JWT token creation/verification, password hashing, `RequireRole` class, `get_current_user` dependency.

**Error Handlers:** Mensajes amigables en espanol por status code (400, 401, 403, 404, 500, etc.).

#### Financial Engine (`financial_engine/`)

Capa separada de calculos financieros puros. Sin dependencias de base de datos.

| Engine | Funcion | Lineas |
|--------|---------|--------|
| `RateEngine` | Conversion EA/EM/NOMINAL/DAILY a tasa mensual | 19 |
| `DebtEngine` | Resumen de deudas, proyeccion de pago | 112 |
| `AmortizationEngine` | Tablas de amortizacion, alertas de vencimiento | 184 |
| `SavingsEngine` | Progreso de metas, proyeccion con interes | 141 |
| `ProjectionEngine` | Escenarios, proyeccion de inversion | 121 |
| `CashFlowEngine` | Flujo de caja historico | 78 |
| `CashFlowProjectionEngine` | Proyeccion de flujo a futuro | 60 |
| `BudgetEngine` | Estado y proyeccion de presupuestos | 160 |
| `NetWorthEngine` | Calculo de patrimonio | 66 |
| `CalendarEngine` | Generacion de eventos recurrentes | 174 |
| `MoneyOperations` | Suma, promedio, porcentaje, interes, amortizacion | 79 |
| `helpers` | `months_between()` | 7 |

**Total:** ~1,100 lineas de codigo puro, deterministic, testeable.

---

## Frontend (`frontend/`)

### Estructura

```
frontend/
  src/
    views/                     # 5 vistas (paginas)
      Login.vue                # Pagina de login
      Resumen.vue              # Panel principal (573 lineas)
      Debts.vue                # Gestion de deudas
      Goals.vue                # Metas de ahorro
      Config.vue               # Perfil y configuracion
    components/                # 43 componentes
      AppLayout.vue            # Layout con sidebar colapsable
      BottomTabBar.vue         # Navegacion inferior (mobile)
      QuickAddFab.vue          # Boton flotante para agregar rapido
      ToastNotification.vue    # Notificaciones toast
      ConfirmDialog.vue        # Dialogo de confirmacion
      SkeletonLoader.vue       # Skeleton de carga
      StatusBadge.vue          # Badge de estado
      FocusTrap.vue            # Trap de foco para modales
      AccountsTab.vue          # Tab de cuentas
      CategoriesTab.vue        # Tab de categorias
      ProfileTab.vue           # Tab de perfil
      ConfigHouseholdTab.vue   # Tab de configuracion del hogar
      debts/                   # Componentes de deudas (9)
      goals/                   # Componentes de metas (12)
      quickadd/                # Componentes del FAB (7)
      budget/                  # Componentes de presupuesto (2)
      calendar/                # Componentes de calendario (2)
      patrimony/               # Componentes de patrimonio
    composables/               # 17 composables reutilizables
      useCurrency.js           # Formato COP
      useFormattedNumber.js    # Formateo de numeros en inputs
      useDashboard.js          # Datos del dashboard
      useGoals.js              # Logica de metas
      useGoalProjection.js     # Proyecciones de metas
      useGoalDate.js           # Fechas de metas
      useBudgets.js            # Logica de presupuestos
      useNotifications.js      # Logica de notificaciones
      useProjections.js        # Proyecciones financieras
      useAgenda.js             # Agenda y calendario
      useCalendarFilters.js    # Filtros del calendario
      useCalendarHelpers.js    # Helpers del calendario
      useCalendarNavigation.js # Navegacion del calendario
      useFinancialHelpers.js   # Helpers financieros generales
      useSmartCalculator.js    # Calculadora inteligente
      useToast.js              # Sistema de toasts
      useConfirm.js            # Dialogo de confirmacion
    stores/                    # 3 stores Pinia
      auth.js                  # Autenticacion y sesion
      goals.js                 # Metas de ahorro
      useCalendar.js           # Calendario y eventos
    services/                  # Capa de servicios HTTP
      api.js                   # Axios con auto-refresh interceptor
      events.js                # Servicios de eventos y obligaciones
    router/
      index.js                 # Vue Router con auth guards
    assets/
      design-tokens.css        # Variables CSS (colores, spacing, shadows, etc.)
      css/
        typography.css         # Estilos de tipografia
        views.css              # Estilos de vistas
    constants/                 # Constantes del frontend
    styles/                    # Estilos globales
  package.json
  vite.config.js
```

---

## Comunicacion Frontend-Backend

- **HTTP Client:** Axios con `baseURL: '/api/v1'`
- **Autenticacion:** Bearer token en header `Authorization`
- **Auto-refresh:** Interceptor de Axios renueva tokens en 401
- **Timeout:** 30 segundos
- **Content-Type:** `application/json`

---

## Migraciones

- **Herramienta:** Alembic
- **Estrategia:** `alembic upgrade head` en startup via lifespan
- **URL:** Pasada por codigo (`cfg.set_main_option()`), no en `alembic.ini`
- **Total:** 11 migraciones versionadas

---

## Testing

### Backend (147 tests)
- **Framework:** pytest + pytest-asyncio + httpx
- **DB de test:** SQLite separada (`test_family_financial.db`)
- **Fixture:** `conftest.py` crea DB con `Base.metadata.create_all` (no Alembic)
- **Archivos:**
  - `test_api.py` — Tests de endpoints (CRUD completo)
  - `test_services.py` — Tests unitarios de services
  - `test_repositories.py` — Tests de repositorios
  - `test_financial_engine.py` — Tests de engines financieros
  - `test_money.py` — Tests del Money VO
  - `test_rate_engine.py` — Tests de conversion de tasas
  - `test_calendar.py` — Tests del calendario
  - `test_calendar_edge.py` — Edge cases del calendario
  - `test_notifications.py` — Tests de notificaciones
  - `test_learning.py` — Tests de deteccion de patrones
  - `test_integration.py` — Tests de integracion
  - `test_security.py` — Tests de seguridad
  - `test_availability.py` — Tests de disponibilidad
  - `test_month_prepare.py` — Tests de preparacion del mes
  - `test_account_update_balance.py` — Tests de actualizacion de balance
  - `test_account_delete.py` — Tests de eliminacion de cuentas

### Frontend (15 archivos de test)
- **Framework:** Vitest + Vue Test Utils
- **Ejecucion:** `npm run test`

---

## Docker

```yaml
# docker-compose.yml
services:
  db:          # PostgreSQL 16 Alpine
  backend:     # FastAPI + uvicorn
```

- **Puerto backend:** 8000
- **Puerto DB:** 5432
- **Volumes:** `pgdata` para persistencia, `./backend:/app` para desarrollo
- **Healthcheck:** `pg_isready` para PostgreSQL

---

## Configuracion

### Variables de Entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| DATABASE_URL | `sqlite+aiosqlite:///family_financial.db` | URL de la DB |
| DATABASE_SYNC_URL | `sqlite:///family_financial.db` | URL sincrona |
| SECRET_KEY | `change-me-in-production` | Clave JWT |
| ALGORITHM | `HS256` | Algoritmo JWT |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Minutos de vida del access token |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | Dias de vida del refresh token |
| CORS_ORIGINS | `["http://localhost:5173"]` | Origenes permitidos |
| DEBUG | `False` | Modo debug |

### Archivos de Configuracion
- `backend/app/config.py` — Settings con Pydantic
- `backend/alembic.ini` — Configuracion de Alembic (sin URL)
- `frontend/vite.config.js` — Configuracion de Vite
- `docker-compose.yml` — Servicios Docker
