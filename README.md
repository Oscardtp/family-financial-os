# Family Financial OS

A comprehensive family financial management platform built with FastAPI (Python) and Vue.js 3.

## Features

- **Accounts**: Manage bank accounts, cash, wallets, and credit cards
- **Transactions**: Track income, expenses, and transfers with categories
- **Budgets**: Set monthly spending limits per category with visual progress
- **Debts**: Track debts with payments, interest rates, and payoff projections
- **Savings**: Set savings goals with contributions and completion forecasts
- **Patrimony**: Register assets and liabilities for net worth tracking
- **Projections**: Cash flow forecasting, debt payoff timeline, scenario simulator
- **Dashboard**: Financial overview with charts (income vs expenses, expense breakdown)
- **Household**: Multi-user support with role-based access (Owner, Member, Viewer)
- **Reports**: CSV export of transactions with date filters
- **Audit Log**: Track who performed each operation

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Alembic |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Vue.js 3, Vite, Pinia, Chart.js, Lucide Icons |
| Auth | JWT (access + refresh tokens), bcrypt |

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

## API Endpoints

| Module | Endpoints |
|--------|-----------|
| Auth | `POST /register`, `POST /login`, `POST /refresh`, `GET /me` |
| Accounts | CRUD at `/accounts` |
| Transactions | CRUD at `/transactions` |
| Categories | CRUD at `/categories` |
| Budgets | CRUD at `/budgets` |
| Debts | CRUD at `/debts`, `POST /debts/{id}/payments` |
| Savings | CRUD at `/savings/goals`, `POST /savings/goals/{id}/contributions` |
| Patrimony | CRUD at `/patrimony/assets`, `/patrimony/liabilities` |
| Dashboard | `GET /dashboard` |
| Projections | `GET /cash-flow`, `GET /debts`, `GET /savings`, `POST /scenario` |
| Household | `GET /household`, `POST /invite`, `PUT /members/{id}/role`, `DELETE /members/{id}` |
| Reports | `GET /reports/transactions/csv` |
| Audit | `GET /audit` |

## Roles

| Role | Permissions |
|------|------------|
| **Owner** | Full access: manage household, invite/remove members, all CRUD |
| **Member** | View data, create/update transactions, manage budgets |
| **Viewer** | Read-only access to all data and reports |

## Testing

```bash
cd backend
pytest
```

## Project Structure

```
family-financial-os/
├── backend/
│   ├── app/
│   │   ├── domain/           # Domain interfaces
│   │   ├── application/      # Application services
│   │   ├── infrastructure/   # SQLAlchemy models & repositories
│   │   └── presentation/     # API routes, schemas, deps
│   ├── alembic/              # Database migrations
│   └── tests/                # Test suite
├── frontend/
│   └── src/
│       ├── components/       # Reusable UI components
│       ├── views/            # Page views
│       ├── stores/           # Pinia state management
│       ├── services/         # API client
│       └── router/           # Vue Router config
└── .opencode/plans/          # Development plans
```
