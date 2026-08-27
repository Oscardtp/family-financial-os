from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.financial_engine.budget_engine import BudgetEngine
from app.presentation.audit_helper import log_action
from app.application.services.dashboard_service import build_budget_item


class BudgetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.budget_repo = SQLAlchemyBudgetRepository(db)
        self.tx_repo = SQLAlchemyTransactionRepository(db)

    async def list(self, household_id: str, month: int | None = None, year: int | None = None):
        today = date.today()
        m = month or today.month
        y = year or today.year
        return await self.budget_repo.get_all(household_id, m, y)

    async def get_status(self, household_id: str, month: int | None = None, year: int | None = None):
        today = date.today()
        m = month or today.month
        y = year or today.year

        budgets = await self.budget_repo.get_all(household_id, m, y)
        end_of_month = (
            date(y, m + 1, 1) - timedelta(days=1)
            if m < 12
            else date(y, 12, 31)
        )
        spending = await self.tx_repo.get_totals_by_category(
            household_id,
            date_from=date(y, m, 1),
            date_to=today if (m == today.month and y == today.year) else end_of_month,
        )

        engine = BudgetEngine()
        result = engine.calculate_budget_status(budgets, spending)

        items = []
        for item in result.items:
            info = build_budget_item(item)
            info["percentage"] = float(item.percentage)
            info["status"] = item.status if item.status != "exceeded" else "over"
            items.append(info)

        return {
            "month": m,
            "year": y,
            "items": items,
            "total_budgeted": float(result.total_budgeted.amount),
            "total_spent": float(result.total_spent.amount),
            "total_remaining": float(result.total_remaining.amount),
        }

    async def create(self, data, user: dict) -> dict:
        repo = self.budget_repo
        existing = await repo.get_by_category_and_period(
            user["household_id"], data.category_id, data.month, data.year
        )
        if existing:
            raise ValueError("Ya hay un presupuesto para esta categoria en este periodo")

        result = await repo.create({
            "category_id": data.category_id,
            "household_id": user["household_id"],
            "amount": float(data.amount),
            "month": data.month,
            "year": data.year,
        })
        await log_action(
            self.db, user["household_id"], user["id"], user["email"],
            "create", "budget", result["id"], result.get("category_id"),
        )
        return result

    async def update(self, budget_id: str, data, user: dict) -> dict:
        repo = self.budget_repo
        budget = await repo.get_by_id(budget_id)
        if not budget or budget["household_id"] != user["household_id"]:
            raise ValueError("Presupuesto no encontrado")

        result = await repo.update({**budget, "amount": float(data.amount)})
        await log_action(
            self.db, user["household_id"], user["id"], user["email"],
            "update", "budget", budget_id, budget.get("category_id"),
        )
        return result

    async def delete(self, budget_id: str, user: dict):
        repo = self.budget_repo
        budget = await repo.get_by_id(budget_id)
        if not budget or budget["household_id"] != user["household_id"]:
            raise ValueError("Presupuesto no encontrado")
        await repo.delete(budget_id)
        await log_action(
            self.db, user["household_id"], user["id"], user["email"],
            "delete", "budget", budget_id, budget.get("category_id"),
        )
