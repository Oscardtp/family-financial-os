from fastapi import APIRouter, Depends
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.debt_repository import SQLAlchemyDebtRepository
from app.infrastructure.repositories.savings_goal_repository import SQLAlchemySavingsGoalRepository
from app.financial_engine.projection_engine import ProjectionEngine, ScenarioAssumptions
from app.financial_engine.debt_engine import DebtEngine
from app.financial_engine.savings_engine import SavingsEngine
from app.domain.value_objects.money import Money
from datetime import date

router = APIRouter(prefix="/projections", tags=["Projections"])


@router.get("/cash-flow", summary="Cash flow projection", description="Projects income and expenses for upcoming months")
async def cash_flow_projection(
    months: int = 12,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    household_id = current_user["household_id"]
    tx_repo = SQLAlchemyTransactionRepository(db)
    today = date.today()
    monthly = await tx_repo.get_monthly_totals(household_id, today.year, today.month)

    engine = ProjectionEngine()
    result = engine.project_scenario(
        current_monthly_income=Money(Decimal(str(monthly["income"]))),
        current_monthly_expenses=Money(Decimal(str(monthly["expense"]))),
        current_debt_balance=Money(Decimal("0")),
        current_savings=Money(Decimal("0")),
        monthly_debt_payment=Money(Decimal("0")),
        months=months,
    )

    return {
        "months": result.months,
        "projections": [
            {
                "month": p["month"],
                "income": str(p["income"].amount),
                "expenses": str(p["expenses"].amount),
                "net_income": str(p["net_income"].amount),
                "cumulative_savings": str(p["cumulative_savings"].amount),
            }
            for p in result.monthly_projections
        ],
        "projected_savings": str(result.projected_savings.amount),
    }


@router.get("/debts", summary="Debt payoff projection", description="Projects when each debt will be paid off")
async def debt_projection(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    household_id = current_user["household_id"]
    debt_repo = SQLAlchemyDebtRepository(db)
    debts = await debt_repo.get_all(household_id)

    engine = DebtEngine()
    projections = []
    for debt in debts:
        payoff = engine.project_payoff(
            balance=Money(Decimal(str(debt["current_balance"]))),
            annual_rate=Decimal(str(debt.get("interest_rate", 0))),
            monthly_payment=Money(Decimal(str(debt.get("minimum_payment", 0)))),
        )
        projections.append({
            "debt_id": debt["id"],
            "name": debt["name"],
            "current_balance": str(debt["current_balance"]),
            "months_to_payoff": payoff["months"],
            "total_paid": str(payoff["total_paid"].amount),
            "total_interest": str(payoff["total_interest"].amount),
        })

    return {"debts": projections}


@router.get("/savings", summary="Savings projection", description="Projects savings goal completion dates")
async def savings_projection(
    months: int = 12,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    household_id = current_user["household_id"]
    savings_repo = SQLAlchemySavingsGoalRepository(db)
    goals = await savings_repo.get_all(household_id)

    engine = SavingsEngine()
    result = engine.calculate_progress(goals)

    return {
        "goals": [
            {
                "id": g.id,
                "name": g.name,
                "target": str(g.target.amount),
                "current": str(g.current.amount),
                "percentage": str(g.percentage),
                "remaining": str(g.remaining.amount),
                "on_track": g.on_track,
                "months_to_goal": g.months_to_goal,
            }
            for g in result.goals
        ],
        "total_target": str(result.total_target.amount),
        "total_current": str(result.total_current.amount),
        "overall_percentage": str(result.overall_percentage),
    }


@router.post("/scenario", summary="Scenario simulator", description="Simulate financial scenarios with custom assumptions")
async def simulate_scenario(
    monthly_income_change: Decimal = Decimal("0"),
    monthly_expense_change: Decimal = Decimal("0"),
    extra_debt_payment: Decimal = Decimal("0"),
    new_monthly_savings: Decimal = Decimal("0"),
    months: int = 12,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    household_id = current_user["household_id"]

    tx_repo = SQLAlchemyTransactionRepository(db)
    debt_repo = SQLAlchemyDebtRepository(db)
    savings_repo = SQLAlchemySavingsGoalRepository(db)

    today = date.today()
    monthly = await tx_repo.get_monthly_totals(household_id, today.year, today.month)
    debts = await debt_repo.get_all(household_id)
    goals = await savings_repo.get_all(household_id)

    total_debt = sum(Decimal(str(d["current_balance"])) for d in debts)
    total_savings = sum(Decimal(str(g["current_amount"])) for g in goals)
    total_min_payment = sum(Decimal(str(d.get("minimum_payment", 0))) for d in debts)

    assumptions = ScenarioAssumptions(
        monthly_income_change=monthly_income_change,
        monthly_expense_change=monthly_expense_change,
        extra_debt_payment=Money(extra_debt_payment) if extra_debt_payment > 0 else None,
        new_monthly_savings=Money(new_monthly_savings) if new_monthly_savings > 0 else None,
    )

    engine = ProjectionEngine()
    result = engine.project_scenario(
        current_monthly_income=Money(Decimal(str(monthly["income"]))),
        current_monthly_expenses=Money(Decimal(str(monthly["expense"]))),
        current_debt_balance=Money(total_debt),
        current_savings=Money(total_savings),
        monthly_debt_payment=Money(total_min_payment),
        months=months,
        assumptions=assumptions,
    )

    return {
        "months": result.months,
        "debt_free_date": result.debt_free_date,
        "projected_net_worth": str(result.projected_net_worth.amount),
        "projected_savings": str(result.projected_savings.amount),
        "projections": [
            {
                "month": p["month"],
                "income": str(p["income"].amount),
                "expenses": str(p["expenses"].amount),
                "net_income": str(p["net_income"].amount),
                "debt_payment": str(p["debt_payment"].amount),
                "remaining_debt": str(p["remaining_debt"].amount),
                "cumulative_savings": str(p["cumulative_savings"].amount),
            }
            for p in result.monthly_projections
        ],
    }
