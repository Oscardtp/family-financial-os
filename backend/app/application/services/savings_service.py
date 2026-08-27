from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.savings_goal_repository import SQLAlchemySavingsGoalRepository
from app.infrastructure.repositories.savings_contribution_repository import SQLAlchemySavingsContributionRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.financial_engine.savings_engine import SavingsEngine
from app.domain.value_objects.money import Money


class SavingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.goal_repo = SQLAlchemySavingsGoalRepository(db)
        self.contrib_repo = SQLAlchemySavingsContributionRepository(db)
        self.tx_repo = SQLAlchemyTransactionRepository(db)

    async def get_summary(self, household_id: str):
        goals = await self.goal_repo.get_all(household_id)

        today = date.today()
        monthly_txs = await self.tx_repo.get_all(
            household_id=household_id,
            date_from=date(today.year, today.month, 1),
            date_to=today,
        )
        monthly_income = Money(Decimal(str(sum(t["amount"] for t in monthly_txs if t["type"] == "income"))))
        monthly_expenses = Money(Decimal(str(sum(t["amount"] for t in monthly_txs if t["type"] == "expense"))))

        engine = SavingsEngine()
        result = engine.calculate_progress(goals, monthly_income, monthly_expenses)

        return {
            "total_target": float(result.total_target.amount),
            "total_current": float(result.total_current.amount),
            "overall_percentage": float(result.overall_percentage),
            "savings_rate": float(result.savings_rate) if result.savings_rate is not None else None,
            "monthly_income": float(monthly_income.amount),
            "monthly_expenses": float(monthly_expenses.amount),
            "goals": [
                {
                    "id": g.id, "name": g.name,
                    "target": float(g.target.amount), "current": float(g.current.amount),
                    "percentage": float(g.percentage), "remaining": float(g.remaining.amount),
                    "on_track": g.on_track, "months_to_goal": g.months_to_goal,
                }
                for g in result.goals
            ],
        }

    async def list_goals(self, household_id: str, skip: int = 0, limit: int = 100):
        return await self.goal_repo.get_all(household_id, skip, limit)

    async def get_goal(self, goal_id: str, household_id: str) -> dict:
        goal = await self.goal_repo.get_by_id(goal_id)
        if not goal or goal["household_id"] != household_id:
            raise ValueError("Meta de ahorro no encontrada")
        return goal

    async def create_goal(self, data, household_id: str) -> dict:
        return await self.goal_repo.create({
            "household_id": household_id,
            **data.model_dump(),
        })

    async def update_goal(self, goal_id: str, data, household_id: str) -> dict:
        goal = await self.get_goal(goal_id, household_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.goal_repo.update({**goal, **update_data})

    async def delete_goal(self, goal_id: str, household_id: str):
        goal = await self.get_goal(goal_id, household_id)
        await self.goal_repo.delete(goal_id)

    async def create_contribution(self, goal_id: str, data, household_id: str) -> dict:
        goal = await self.get_goal(goal_id, household_id)

        contribution = await self.contrib_repo.create({
            "goal_id": goal_id,
            "amount": data.amount,
            "contribution_date": data.contribution_date,
        })

        new_amount = goal["current_amount"] + data.amount
        await self.goal_repo.update({**goal, "current_amount": new_amount})

        return contribution

    async def list_contributions(self, goal_id: str, household_id: str, skip: int = 0, limit: int = 100):
        await self.get_goal(goal_id, household_id)
        return await self.contrib_repo.get_by_goal_id(goal_id, skip, limit)

    def project_goal(self, data):
        engine = SavingsEngine()
        return engine.calculate_goal_projection(
            current_amount=data.current_amount,
            monthly_contribution=data.monthly_contribution,
            target_amount=data.target_amount,
            expected_return_rate=data.expected_return_rate,
            horizon_months=data.horizon_months,
        )
