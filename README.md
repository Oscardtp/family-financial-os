# Family Financial OS

Sistema operativo financiero familiar para hogares colombianos. Administra tu economía real de manera simple, privada y rápida.

## Características

- **Dashboard inteligente**: Resumen financiero con alertas, presupuestos y movimientos próximos
- **Gestión de deudas**: Amortización, pagos, proyecciones y alertas de vencimiento
- **Metas de ahorro**: Simulación de escenarios, contribuciones y proyecciones
- **Calendario financiero**: Eventos, obligaciones y pagos recurrentes en FullCalendar
- **Presupuestos**: Seguimiento por categoría con alertas de excedido
- **Multi-tenant**: Datos aislados por hogar con roles (Owner, Member, Viewer)
- **Motor financiero**: Cálculos de tasas (EA, EM, nominal, diaria), amortización y proyecciones

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| Frontend | Vue.js 3 (Composition API), Pinia, Vue Router, Vite 5, Chart.js |
| Base de datos | PostgreSQL 16 (producción) / SQLite (desarrollo) |
| Auth | JWT (python-jose), bcrypt, passlib |
| Testing | pytest (backend), Vitest + Vue Test Utils (frontend) |
| Deploy | Docker, docker-compose |

## Inicio Rápido

### Requisitos

- Python 3.12+
- Node.js 18+
- Docker (opcional, para PostgreSQL)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/family-financial-os.git
cd family-financial-os

# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python init_db.py             # Aplica migraciones y crea la DB

# Frontend
cd ../frontend
npm install
```

### Ejecutar

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Abrir http://localhost:5173

### Registrar Primer Usuario

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@familia.com","name":"Administrador","password":"familia123"}'
```

## Estructura del Proyecto

```
family-financial-os/
├── backend/
│   ├── app/
│   │   ├── domain/             # Value Objects, Entities, Exceptions
│   │   ├── application/        # Services, Repository Interfaces
│   │   ├── infrastructure/     # SQLAlchemy Models, Repository Impls
│   │   ├── presentation/       # Routers, Schemas, DI, Error Handlers
│   │   └── financial_engine/   # Cálculos financieros puros
│   ├── alembic/                # Migraciones versionadas
│   ├── tests/                  # 66 tests pytest
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/              # 5 vistas
│   │   ├── components/         # 43 componentes
│   │   ├── composables/        # 17 composables
│   │   ├── stores/             # 3 stores Pinia
│   │   └── services/           # API client + events
│   └── vite.config.js
├── docker-compose.yml
└── AGENTS.md
```

## API

Ver `AGENTS.md` para la lista completa de endpoints.

**Auth:**
- `POST /api/v1/auth/register` — Registro
- `POST /api/v1/auth/login` — Login
- `POST /api/v1/auth/refresh` — Renovar tokens
- `GET /api/v1/auth/me` — Perfil

**Finanzas:**
- `GET/POST /api/v1/accounts` — Cuentas
- `GET/POST /api/v1/transactions` — Transacciones
- `GET/POST /api/v1/debts` — Deudas
- `GET/POST /api/v1/savings/goals` — Metas de ahorro
- `GET /api/v1/dashboard` — Resumen financiero

## Testing

```bash
# Backend (66 tests)
cd backend
python -m pytest tests/ -x -q

# Frontend
cd frontend
npm run test
```

## Base de Datos

### Migraciones

```bash
cd backend

# Aplicar migraciones
python init_db.py

# Reset completo (solo desarrollo)
python init_db.py reset

# Crear nueva migración
alembic revision --autogenerate -m "descripcion del cambio"
```

### Esquema

19 tablas principales:
- `households`, `users` — Multi-tenant
- `accounts`, `categories`, `transactions` — Finanzas básicas
- `debts`, `debt_payments`, `debt_payment_overrides` — Deudas
- `savings_goals`, `savings_contributions` — Metas
- `budgets` — Presupuestos
- `recurring_payments` — Pagos recurrentes
- `financial_obligations`, `financial_events` — Calendario
- `notifications`, `audit_logs` — Sistema
- `assets`, `liabilities` — Patrimonio
- `category_account_preferences` — Preferencias

## Arquitectura

Ver `architecture-decisions.md` para las decisiones técnicas (ADRs).

- **Clean Architecture**: domain → application → infrastructure → presentation
- **Multi-tenant**: Aislamiento por `household_id`
- **Money = Decimal**: Nunca `float` para dinero
- **RateEngine**: Conversiones de tasa centralizadas (EA, EM, NOMINAL, DAILY)
- **TDD**: Test fallido primero, código después

## Variables de Entorno

Copiar `.env.example` a `.env`:

```env
# Seguridad
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=true

# Base de datos (opcional, default SQLite)
DATABASE_URL=sqlite+aiosqlite:///path/to/db.sqlite
DATABASE_SYNC_URL=sqlite:///path/to/db.sqlite

# PostgreSQL (producción)
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
# DATABASE_SYNC_URL=postgresql://user:pass@localhost:5432/dbname
```

## Docker

```bash
# Levantar PostgreSQL + Backend
docker compose up -d

# Detener
docker compose down
```

## Known Issues

Ver `known-issues.md` para issues conocidos y su estado.

## Licencia

Proyecto privado. Todos los derechos reservados.
