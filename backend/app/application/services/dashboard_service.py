from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.debt_repository import SQLAlchemyDebtRepository
from app.infrastructure.repositories.savings_goal_repository import SQLAlchemySavingsGoalRepository
from app.infrastructure.repositories.asset_repository import SQLAlchemyAssetRepository
from app.infrastructure.repositories.liability_repository import SQLAlchemyLiabilityRepository
from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.infrastructure.repositories.recurring_payment_repository import SQLAlchemyRecurringPaymentRepository
from app.presentation.schemas.schemas import RecurringPaymentResponse, SavingsSummary, SavingsGoalSummary
from app.financial_engine.budget_engine import BudgetEngine


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repo = SQLAlchemyAccountRepository(db)
        self.tx_repo = SQLAlchemyTransactionRepository(db)
        self.debt_repo = SQLAlchemyDebtRepository(db)
        self.savings_repo = SQLAlchemySavingsGoalRepository(db)
        self.asset_repo = SQLAlchemyAssetRepository(db)
        self.liability_repo = SQLAlchemyLiabilityRepository(db)
        self.budget_repo = SQLAlchemyBudgetRepository(db)
        self.recurring_repo = SQLAlchemyRecurringPaymentRepository(db)

    async def get_summary(self, user: dict):
        household_id = user["household_id"]

        total_balance = await self._get_total_balance(household_id)
        monthly_income, monthly_expenses = await self._get_monthly_flow(household_id)
        total_debt = await self.debt_repo.get_total_balance(household_id)
        total_savings = await self._get_total_savings(household_id)
        net_worth = await self._get_net_worth(household_id, total_balance)
        recent_txs = await self.tx_repo.get_all(household_id=household_id, limit=10)

        budget_status = await self._get_budget_status(household_id)
        upcoming = await self._get_upcoming_payments(household_id)
        savings_summary = await self._get_savings_summary(household_id, total_savings)
        financial_alert = await self._build_financial_alert(household_id, monthly_income)

        from app.presentation.schemas.schemas import DashboardResponse
        return DashboardResponse(
            total_balance=total_balance,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            net_monthly=monthly_income - monthly_expenses,
            total_debt=total_debt,
            total_savings=total_savings,
            net_worth=net_worth,
            recent_transactions=recent_txs,
            budget_status=budget_status,
            upcoming_payments=upcoming,
            savings_summary=savings_summary,
            financial_alert=financial_alert,
        )

    async def _get_total_balance(self, household_id: str) -> Decimal:
        accounts = await self.account_repo.get_all(household_id)
        return sum(a["balance"] for a in accounts if a["type"] != "credit_card")

    async def _get_monthly_flow(self, household_id: str) -> tuple[Decimal, Decimal]:
        today = date.today()
        end_of_month = (
            date(today.year, today.month + 1, 1) - timedelta(days=1)
            if today.month < 12
            else date(today.year, 12, 31)
        )
        monthly_txs = await self.tx_repo.get_all(
            household_id=household_id,
            date_from=date(today.year, today.month, 1),
            date_to=end_of_month,
        )
        income = sum(t["amount"] for t in monthly_txs if t["type"] == "income")
        expenses = sum(t["amount"] for t in monthly_txs if t["type"] == "expense")
        return income, expenses

    async def _get_total_savings(self, household_id: str) -> Decimal:
        goals = await self.savings_repo.get_all(household_id)
        return sum(g["current_amount"] for g in goals)

    async def _get_net_worth(self, household_id: str, balance: Decimal) -> Decimal:
        total_assets = await self.asset_repo.get_total_value(household_id)
        total_liabilities = await self.liability_repo.get_total_balance(household_id)
        return total_assets + balance - total_liabilities

    async def _get_budget_status(self, household_id: str) -> list[dict]:
        today = date.today()
        budgets = await self.budget_repo.get_all(household_id, today.month, today.year)
        end_of_month = (
            date(today.year, today.month + 1, 1) - timedelta(days=1)
            if today.month < 12
            else date(today.year, 12, 31)
        )
        spending = await self.tx_repo.get_totals_by_category(
            household_id,
            date_from=date(today.year, today.month, 1),
            date_to=end_of_month,
        )
        engine = BudgetEngine()
        result = engine.calculate_budget_status(budgets, spending)
        return [build_budget_item(item) for item in result.items]

    async def _get_upcoming_payments(self, household_id: str) -> list:
        upcoming = await self.recurring_repo.get_active(household_id)
        return [
            RecurringPaymentResponse(
                id=p["id"], household_id=p["household_id"],
                account_id=p["account_id"], category_id=p.get("category_id"),
                name=p["name"], amount=p["amount"], type=p["type"],
                frequency=p["frequency"], day_of_month=p["day_of_month"],
                next_due_date=p["next_due_date"], is_active=p["is_active"],
                description=p.get("description"), created_at=p["created_at"],
            )
            for p in upcoming[:5]
        ]

    async def _get_savings_summary(self, household_id: str, total_savings) -> SavingsSummary:
        goals = await self.savings_repo.get_all(household_id)
        return SavingsSummary(
            total=total_savings,
            goals=[
                SavingsGoalSummary(
                    name=g["name"], current=g["current_amount"],
                    target=g["target_amount"], target_date=g.get("target_date"),
                )
                for g in goals
            ],
        )

    async def _build_financial_alert(self, household_id: str, monthly_income: Decimal) -> dict | None:
        debts = await self.debt_repo.get_all(household_id)
        active_debts = [d for d in debts if d["status"] == "active"]
        paused_debts = [d for d in debts if d["status"] == "paused"]
        total_monthly_payment = sum(d.get("minimum_payment", 0) for d in active_debts)

        if monthly_income > 0 and total_monthly_payment > monthly_income:
            diff = total_monthly_payment - monthly_income
            alert_msg = f"Este mes necesitas ${diff:,.0f} mas de lo que generas para cubrir todas tus deudas"
            if paused_debts:
                paused_total = sum(d.get("current_balance", 0) for d in paused_debts)
                alert_msg += f". Tiene {len(paused_debts)} deuda(s) pausada(s) por ${paused_total:,.0f} que siguen pendientes."
            return {
                "type": "critical" if diff > monthly_income * Decimal("0.5") else "warning",
                "message": alert_msg,
                "total_needed": total_monthly_payment,
                "income": monthly_income,
                "deficit": diff,
                "options": [
                    "Usar ahorros disponibles",
                    "Posponer pagos no criticos",
                    "Buscar ingresos adicionales",
                ],
            }
        elif paused_debts:
            paused_total = sum(d.get("current_balance", 0) for d in paused_debts)
            return {
                "type": "info",
                "message": f"Tiene {len(paused_debts)} deuda(s) pausada(s) por ${paused_total:,.0f}. Considere reactivarlas cuando pueda.",
                "total_needed": 0,
                "income": monthly_income,
                "deficit": 0,
                "options": [],
            }
        return None


def build_budget_item(item) -> dict:
    budgeted = float(item.budgeted.amount)
    spent = float(item.spent.amount)
    status = item.status
    message = None
    if status == "exceeded":
        diff = spent - budgeted
        pct = ((diff / budgeted) * 100) if budgeted > 0 else 0
        message = f"{item.category_name} excedio ${diff:,.0f} ({pct:.1f}%). Considere revisar el presupuesto."
    elif status == "warning":
        pct = ((spent / budgeted) * 100) if budgeted > 0 else 0
        remaining = budgeted - spent
        message = f"{item.category_name} va al {pct:.0f}% del presupuesto. Le quedan ${remaining:,.0f}."
    else:
        remaining = budgeted - spent
        message = f"{item.category_name} esta dentro del presupuesto. Le quedan ${remaining:,.0f}."
    return {
        "category": item.category_name,
        "budgeted": budgeted,
        "spent": spent,
        "status": status,
        "message": message,
    }
