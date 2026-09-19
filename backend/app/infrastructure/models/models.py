import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Integer, Date, Text
from app.database import Base


class HouseholdModel(Base):
    __tablename__ = "households"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    base_currency = Column(String(3), default="COP")
    timezone = Column(String(50), default="America/Bogota")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="member")
    household_id = Column(String(36), ForeignKey("households.id"), nullable=True)
    status = Column(String(20), default="active")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    institution = Column(String(255), nullable=True)
    balance = Column(Numeric(15, 2), default=0)
    opening_balance = Column(Numeric(15, 2), default=0)
    credit_limit = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="COP")
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    parent_id = Column(String(36), nullable=True)
    is_active = Column(Boolean, default=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    type = Column(String(20), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    status = Column(String(20), default="completed")
    to_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    period = Column(String(20), default="monthly")
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class DebtModel(Base):
    __tablename__ = "debts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), default="loan")
    creditor = Column(String(255), nullable=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    total_amount = Column(Numeric(15, 2), nullable=False)
    current_balance = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), default=0)
    interest_rate_type = Column(String(20), default="EA")
    minimum_payment = Column(Numeric(15, 2), default=0)
    due_day = Column(Integer, default=1)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(50), default="active")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class DebtPaymentModel(Base):
    __tablename__ = "debt_payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    debt_id = Column(String(36), ForeignKey("debts.id"), nullable=False)
    household_id = Column(String(36), ForeignKey("households.id"), nullable=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    principal = Column(Numeric(15, 2), nullable=True)
    interest = Column(Numeric(15, 2), nullable=True)
    fees_amount = Column(Numeric(15, 2), default=0)
    payment_date = Column(Date, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_reversed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DebtPaymentOverrideModel(Base):
    __tablename__ = "debt_payment_overrides"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    debt_id = Column(String(36), ForeignKey("debts.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    is_paid = Column(Boolean, default=True, nullable=False)
    marked_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    marked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SavingsGoalModel(Base):
    __tablename__ = "savings_goals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    name = Column(String(255), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0)
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    contribution_frequency = Column(String(20), default="monthly")
    monthly_contribution = Column(Numeric(15, 2), nullable=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    status = Column(String(20), default="active")
    priority = Column(String(20), default="medium")
    description = Column(Text, nullable=True)
    goal_type = Column(String(20), default="savings")
    expected_return_rate = Column(Numeric(5, 2), nullable=True)
    horizon_months = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SavingsContributionModel(Base):
    __tablename__ = "savings_contributions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String(36), ForeignKey("savings_goals.id"), nullable=False)
    household_id = Column(String(36), ForeignKey("households.id"), nullable=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    contribution_date = Column(Date, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AssetModel(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")
    valuation_date = Column(Date, nullable=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    purchase_date = Column(Date, nullable=True)
    status = Column(String(20), default="active")


class LiabilityModel(Base):
    __tablename__ = "liabilities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    current_balance = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")
    valuation_date = Column(Date, nullable=True)
    interest_rate = Column(Numeric(5, 2), default=0)
    interest_rate_type = Column(String(20), default="EA")
    monthly_payment = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default="active")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False)
    user_email = Column(String(255), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=True)
    entity_name = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RecurringPaymentModel(Base):
    __tablename__ = "recurring_payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(String(20), nullable=False, default="expense")
    frequency = Column(String(20), nullable=False, default="monthly")
    interval = Column(Integer, default=1)
    day_of_month = Column(Integer, default=1)
    start_date = Column(Date, nullable=True)
    next_due_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="active")
    description = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CategoryAccountPreferenceModel(Base):
    __tablename__ = "category_account_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FinancialObligationModel(Base):
    __tablename__ = "financial_obligations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    source = Column(String(20), nullable=False)
    source_id = Column(String(36), nullable=True)
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")
    frequency = Column(String(20), default="monthly")
    anchor_day = Column(Integer, nullable=True)
    recommended_offset_days = Column(Integer, default=5)
    cutoff_offset_days = Column(Integer, nullable=True)
    reminder_days_before = Column(Integer, default=3)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    responsible_member_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    confidence = Column(Integer, default=100)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FinancialEventModel(Base):
    __tablename__ = "financial_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    source = Column(String(20), nullable=False)
    source_id = Column(String(36), nullable=True)
    type = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")
    due_date = Column(Date, nullable=False)
    recommended_date = Column(Date, nullable=True)
    cutoff_date = Column(Date, nullable=True)
    status = Column(String(20), default="pending")
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    responsible_member_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_recurrent = Column(Boolean, default=False)
    recurrence_group_id = Column(String(36), nullable=True)
    reminder_days_before = Column(Integer, default=3)
    notes = Column(Text, nullable=True)
    confirmed = Column(Boolean, default=True)
    paid_at = Column(DateTime, nullable=True)
    paid_amount = Column(Numeric(15, 2), nullable=True)
    paid_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    obligation_id = Column(String(36), nullable=True, index=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    visibility = Column(String(12), default="confirmed")
    confidence = Column(Integer, default=100)
    payment_method = Column(String(12), nullable=True)
    consequence_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AccountBalanceHistoryModel(Base):
    __tablename__ = "account_balance_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=True, index=True)
    balance_before = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    change_amount = Column(Numeric(15, 2), nullable=False)
    change_type = Column(String(20), nullable=False)  # income, expense, transfer, adjustment
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AmortizationScheduleModel(Base):
    __tablename__ = "amortization_schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    debt_id = Column(String(36), ForeignKey("debts.id"), nullable=False, index=True)
    month_number = Column(Integer, nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(Numeric(15, 2), nullable=False)
    principal_portion = Column(Numeric(15, 2), nullable=False)
    interest_portion = Column(Numeric(15, 2), nullable=False)
    remaining_balance = Column(Numeric(15, 2), nullable=False)
    cumulative_interest = Column(Numeric(15, 2), nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DetectedPatternModel(Base):
    __tablename__ = "detected_patterns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # income, expense
    avg_amount = Column(Numeric(15, 2), nullable=False)
    avg_day_of_month = Column(Integer, nullable=True)
    frequency = Column(String(20), nullable=False)  # monthly, weekly, biweekly
    occurrences = Column(Integer, nullable=False, default=1)
    confidence = Column(Integer, nullable=False, default=50)  # 0-100
    source = Column(String(50), nullable=False)  # transaction, event, manual
    source_id = Column(String(36), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    first_seen = Column(Date, nullable=False)
    last_seen = Column(Date, nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    is_rejected = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TransferModel(Base):
    __tablename__ = "transfers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    from_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="COP")
    transaction_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class HouseholdMemberModel(Base):
    __tablename__ = "household_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20), default="member")
    status = Column(String(20), default="active")
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ImportBatchModel(Base):
    __tablename__ = "import_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    household_id = Column(String(36), ForeignKey("households.id"), nullable=False, index=True)
    source_file = Column(String(500), nullable=False)
    imported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), default="pending")
    records_detected = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    error_report = Column(Text, nullable=True)


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    jti = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
