import pytest
from decimal import Decimal
from datetime import date
from app.domain.value_objects.money import Money
from app.financial_engine.money_operations import MoneyOperations
from app.financial_engine.cash_flow import CashFlowEngine
from app.financial_engine.budget_engine import BudgetEngine
from app.financial_engine.debt_engine import DebtEngine
from app.financial_engine.savings_engine import SavingsEngine
from app.financial_engine.net_worth_engine import NetWorthEngine
from app.financial_engine.projection_engine import ProjectionEngine, ScenarioAssumptions


class TestMoneyOperations:
    def test_sum_amounts(self):
        amounts = [Money("100"), Money("200"), Money("300")]
        assert MoneyOperations.sum_amounts(amounts) == Money("600")

    def test_sum_empty(self):
        assert MoneyOperations.sum_amounts([]) == Money.zero()

    def test_average(self):
        amounts = [Money("100"), Money("200"), Money("300")]
        assert MoneyOperations.average(amounts) == Money("200")

    def test_percentage(self):
        assert MoneyOperations.percentage(Money("25"), Money("100")) == Decimal("25.00")

    def test_percentage_zero_whole(self):
        assert MoneyOperations.percentage(Money("25"), Money("0")) == Decimal("0.00")

    def test_apply_interest(self):
        result = MoneyOperations.apply_interest(Money("1000"), Decimal("12"), 1, "EA")
        assert result.amount == Decimal("1009.49")

    def test_apply_interest_em(self):
        result = MoneyOperations.apply_interest(Money("1000"), Decimal("12"), 1, "EM")
        assert result.amount == Decimal("1120.00")

    def test_amortize_payment(self):
        result = MoneyOperations.amortize_payment(Money("1000"), Decimal("12"), 12, 1, "EA")
        assert result["payment"].is_positive()
        assert result["principal"].is_positive()
        assert result["interest"].is_positive()


class TestCashFlowEngine:
    def test_calculate_cash_flow(self):
        engine = CashFlowEngine()
        transactions = [
            {"type": "income", "amount": "5000", "date": date(2026, 1, 15)},
            {"type": "expense", "amount": "2000", "date": date(2026, 1, 20)},
            {"type": "expense", "amount": "500", "date": date(2026, 1, 25)},
        ]
        result = engine.calculate_cash_flow(transactions, date(2026, 1, 1), date(2026, 1, 31))
        assert result.total_income == Money("5000")
        assert result.total_expenses == Money("2500")
        assert result.net_cash_flow == Money("2500")

    def test_project_cash_flow(self):
        engine = CashFlowEngine()
        result = engine.project_cash_flow(
            monthly_income=Money("5000"),
            monthly_expenses=Money("3000"),
            months=3,
        )
        assert len(result) == 3
        assert result[0]["net"] == Money("2000")
        assert result[0]["cumulative"] == Money("2000")


class TestBudgetEngine:
    def test_calculate_budget_status(self):
        engine = BudgetEngine()
        budgets = [
            {"category_id": "cat1", "amount": "800"},
            {"category_id": "cat2", "amount": "300"},
        ]
        spending = [
            {"category_id": "cat1", "category_name": "Food", "total": "620", "type": "expense"},
            {"category_id": "cat2", "category_name": "Transport", "total": "250", "type": "expense"},
        ]
        result = engine.calculate_budget_status(budgets, spending)
        assert result.total_budgeted == Money("1100")
        assert result.total_spent == Money("870")
        assert len(result.items) == 2

    def test_detect_overruns(self):
        engine = BudgetEngine()
        from app.financial_engine.budget_engine import BudgetStatusItem, BudgetStatusResult
        result = BudgetStatusResult(
            items=[
                BudgetStatusItem("1", "Food", Money("800"), Money("620"), Money("180"), Decimal("77.50"), "ok"),
                BudgetStatusItem("2", "Fun", Money("150"), Money("170"), Money("-20"), Decimal("113.33"), "exceeded"),
            ],
            total_budgeted=Money("950"),
            total_spent=Money("790"),
            total_remaining=Money("160"),
        )
        overruns = engine.detect_overruns(result)
        assert len(overruns) == 1
        assert overruns[0].category_name == "Fun"


class TestDebtEngine:
    def test_calculate_summary(self):
        engine = DebtEngine()
        debts = [
            {"id": "1", "name": "Credit Card", "creditor": "Bank",
             "total_amount": "1000", "current_balance": "500",
             "interest_rate": "18", "minimum_payment": "50", "status": "active"},
        ]
        result = engine.calculate_summary(debts)
        assert result.total_original == Money("1000")
        assert result.total_balance == Money("500")
        assert result.overall_progress == Decimal("50.00")

    def test_project_payoff(self):
        engine = DebtEngine()
        result = engine.project_payoff(
            balance=Money("1000"),
            annual_rate=Decimal("12"),
            monthly_payment=Money("100"),
        )
        assert result["months"] > 0
        assert result["total_paid"].is_positive()

    def test_project_payoff_em_rate(self):
        engine = DebtEngine()
        result_ea = engine.project_payoff(
            balance=Money("1000"),
            annual_rate=Decimal("12"),
            monthly_payment=Money("100"),
        )
        result_em = engine.project_payoff(
            balance=Money("1000"),
            annual_rate=Decimal("12"),
            monthly_payment=Money("200"),
            rate_type="EM",
        )
        assert result_em["months"] > 0
        assert result_em["total_paid"].is_positive()
        assert result_em["months"] != result_ea["months"]


class TestSavingsEngine:
    def test_calculate_progress(self):
        engine = SavingsEngine()
        goals = [
            {"id": "1", "name": "Emergency Fund", "target_amount": "5000", "current_amount": "2500"},
            {"id": "2", "name": "Vacation", "target_amount": "2000", "current_amount": "2000"},
        ]
        result = engine.calculate_progress(goals)
        assert result.total_target == Money("7000")
        assert result.total_current == Money("4500")
        assert len(result.goals) == 2


class TestNetWorthEngine:
    def test_calculate_net_worth(self):
        engine = NetWorthEngine()
        assets = [{"id": "1", "name": "Car", "type": "vehicle", "value": "30000"}]
        liabilities = [{"id": "1", "name": "Car Loan", "type": "loan", "current_balance": "15000"}]
        result = engine.calculate_net_worth(assets, liabilities)
        assert result.total_assets == Money("30000")
        assert result.total_liabilities == Money("15000")
        assert result.net_worth == Money("15000")


class TestProjectionEngine:
    def test_project_scenario(self):
        engine = ProjectionEngine()
        result = engine.project_scenario(
            current_monthly_income=Money("5000"),
            current_monthly_expenses=Money("3000"),
            current_debt_balance=Money("10000"),
            current_savings=Money("2000"),
            monthly_debt_payment=Money("500"),
            months=12,
        )
        assert result.months == 12
        assert len(result.monthly_projections) == 12
        assert result.projected_savings.is_positive()

    def test_with_assumptions(self):
        engine = ProjectionEngine()
        assumptions = ScenarioAssumptions(
            monthly_income_change=Decimal("5"),
            monthly_expense_change=Decimal("-10"),
        )
        result = engine.project_scenario(
            current_monthly_income=Money("5000"),
            current_monthly_expenses=Money("3000"),
            current_debt_balance=Money("5000"),
            current_savings=Money("1000"),
            monthly_debt_payment=Money("500"),
            months=6,
            assumptions=assumptions,
        )
        assert result.projected_savings > Money("1000")
