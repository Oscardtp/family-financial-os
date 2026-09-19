"""Add missing columns to existing entities - Phase 2 schema cleanup

Revision ID: a1b2c3d4e5f6
Revises: l5m6n7o8p9q0
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "l5m6n7o8p9q0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Household ---
    op.add_column("households", sa.Column("base_currency", sa.String(3), server_default="COP"))
    op.add_column("households", sa.Column("timezone", sa.String(50), server_default="America/Bogota"))
    op.add_column("households", sa.Column("status", sa.String(20), server_default="active"))
    op.add_column("households", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))

    # --- User ---
    op.add_column("users", sa.Column("status", sa.String(20), server_default="active"))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))

    # --- Account ---
    op.add_column("accounts", sa.Column("institution", sa.String(255), nullable=True))
    op.add_column("accounts", sa.Column("opening_balance", sa.Numeric(15, 2), server_default="0"))
    op.add_column("accounts", sa.Column("credit_limit", sa.Numeric(15, 2), nullable=True))
    op.add_column("accounts", sa.Column("status", sa.String(20), server_default="active"))
    op.add_column("accounts", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))

    # --- Category ---
    op.add_column("categories", sa.Column("parent_id", sa.String(36), nullable=True))
    op.add_column("categories", sa.Column("is_active", sa.Boolean(), server_default="true"))
    op.add_column("categories", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.add_column("categories", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))

    # --- Transaction ---
    op.add_column("transactions", sa.Column("household_id", sa.String(36), nullable=True))
    op.add_column("transactions", sa.Column("currency", sa.String(3), server_default="COP"))
    op.add_column("transactions", sa.Column("status", sa.String(20), server_default="completed"))
    op.add_column("transactions", sa.Column("created_by", sa.String(36), nullable=True))
    op.add_column("transactions", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))

    # --- Debt ---
    op.add_column("debts", sa.Column("type", sa.String(50), server_default="loan"))
    op.add_column("debts", sa.Column("account_id", sa.String(36), nullable=True))
    op.add_column("debts", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.add_column("debts", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))

    # --- DebtPayment ---
    op.add_column("debt_payments", sa.Column("household_id", sa.String(36), nullable=True))
    op.add_column("debt_payments", sa.Column("transaction_id", sa.String(36), nullable=True))
    op.add_column("debt_payments", sa.Column("fees_amount", sa.Numeric(15, 2), server_default="0"))
    op.add_column("debt_payments", sa.Column("created_by", sa.String(36), nullable=True))
    op.add_column("debt_payments", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))

    # --- Budget ---
    op.add_column("budgets", sa.Column("period", sa.String(20), server_default="monthly"))
    op.add_column("budgets", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.add_column("budgets", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))

    # --- SavingsGoal ---
    op.add_column("savings_goals", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("savings_goals", sa.Column("contribution_frequency", sa.String(20), server_default="monthly"))
    op.add_column("savings_goals", sa.Column("account_id", sa.String(36), nullable=True))
    op.add_column("savings_goals", sa.Column("status", sa.String(20), server_default="active"))
    op.add_column("savings_goals", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.add_column("savings_goals", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))

    # --- SavingsContribution (GoalContribution) ---
    op.add_column("savings_contributions", sa.Column("household_id", sa.String(36), nullable=True))
    op.add_column("savings_contributions", sa.Column("transaction_id", sa.String(36), nullable=True))
    op.add_column("savings_contributions", sa.Column("created_by", sa.String(36), nullable=True))
    op.add_column("savings_contributions", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))

    # --- Asset ---
    op.add_column("assets", sa.Column("currency", sa.String(3), server_default="COP"))
    op.add_column("assets", sa.Column("valuation_date", sa.Date(), nullable=True))
    op.add_column("assets", sa.Column("account_id", sa.String(36), nullable=True))
    op.add_column("assets", sa.Column("status", sa.String(20), server_default="active"))

    # --- Liability ---
    op.add_column("liabilities", sa.Column("currency", sa.String(3), server_default="COP"))
    op.add_column("liabilities", sa.Column("valuation_date", sa.Date(), nullable=True))
    op.add_column("liabilities", sa.Column("status", sa.String(20), server_default="active"))

    # --- RecurringPayment ---
    op.add_column("recurring_payments", sa.Column("interval", sa.Integer(), server_default="1"))
    op.add_column("recurring_payments", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("recurring_payments", sa.Column("end_date", sa.Date(), nullable=True))
    op.add_column("recurring_payments", sa.Column("status", sa.String(20), server_default="active"))
    op.add_column("recurring_payments", sa.Column("created_by", sa.String(36), nullable=True))
    op.add_column("recurring_payments", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))


def downgrade() -> None:
    # RecurringPayment
    op.drop_column("recurring_payments", "updated_at")
    op.drop_column("recurring_payments", "created_by")
    op.drop_column("recurring_payments", "status")
    op.drop_column("recurring_payments", "end_date")
    op.drop_column("recurring_payments", "start_date")
    op.drop_column("recurring_payments", "interval")

    # Liability
    op.drop_column("liabilities", "status")
    op.drop_column("liabilities", "valuation_date")
    op.drop_column("liabilities", "currency")

    # Asset
    op.drop_column("assets", "status")
    op.drop_column("assets", "account_id")
    op.drop_column("assets", "valuation_date")
    op.drop_column("assets", "currency")

    # SavingsContribution
    op.drop_column("savings_contributions", "created_at")
    op.drop_column("savings_contributions", "created_by")
    op.drop_column("savings_contributions", "transaction_id")
    op.drop_column("savings_contributions", "household_id")

    # SavingsGoal
    op.drop_column("savings_goals", "updated_at")
    op.drop_column("savings_goals", "created_at")
    op.drop_column("savings_goals", "status")
    op.drop_column("savings_goals", "account_id")
    op.drop_column("savings_goals", "contribution_frequency")
    op.drop_column("savings_goals", "start_date")

    # Budget
    op.drop_column("budgets", "updated_at")
    op.drop_column("budgets", "created_at")
    op.drop_column("budgets", "period")

    # DebtPayment
    op.drop_column("debt_payments", "created_at")
    op.drop_column("debt_payments", "created_by")
    op.drop_column("debt_payments", "fees_amount")
    op.drop_column("debt_payments", "transaction_id")
    op.drop_column("debt_payments", "household_id")

    # Debt
    op.drop_column("debts", "updated_at")
    op.drop_column("debts", "created_at")
    op.drop_column("debts", "account_id")
    op.drop_column("debts", "type")

    # Transaction
    op.drop_column("transactions", "updated_at")
    op.drop_column("transactions", "created_by")
    op.drop_column("transactions", "status")
    op.drop_column("transactions", "currency")
    op.drop_column("transactions", "household_id")

    # Category
    op.drop_column("categories", "updated_at")
    op.drop_column("categories", "created_at")
    op.drop_column("categories", "is_active")
    op.drop_column("categories", "parent_id")

    # Account
    op.drop_column("accounts", "updated_at")
    op.drop_column("accounts", "status")
    op.drop_column("accounts", "credit_limit")
    op.drop_column("accounts", "opening_balance")
    op.drop_column("accounts", "institution")

    # User
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "status")

    # Household
    op.drop_column("households", "updated_at")
    op.drop_column("households", "status")
    op.drop_column("households", "timezone")
    op.drop_column("households", "base_currency")
