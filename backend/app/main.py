import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from contextlib import asynccontextmanager
from alembic.config import Config
from alembic import command
from pathlib import Path
from app.config import get_settings, DB_FILE
from app.database import engine
from app.presentation.v1 import (
    auth, accounts, transactions, categories, budgets, debts, savings,
    patrimony, dashboard, projections, household, reports, audit,
    recurring_payments, notifications, preferences, events, obligations, coach, month,
)
from app.presentation.error_handlers import validation_error_handler, http_error_handler, generic_error_handler

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

settings = get_settings()


def _run_migrations():
    cfg = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{DB_FILE}")
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: running database migrations...")
    await asyncio.to_thread(_run_migrations)
    print("Database migrations applied")
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(500, generic_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(debts.router, prefix="/api/v1")
app.include_router(savings.router, prefix="/api/v1")
app.include_router(patrimony.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(projections.router, prefix="/api/v1")
app.include_router(household.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(recurring_payments.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(obligations.router, prefix="/api/v1")
app.include_router(coach.router, prefix="/api/v1")
app.include_router(month.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
