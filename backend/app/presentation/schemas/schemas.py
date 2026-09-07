from pydantic import BaseModel, EmailStr, Field
from datetime import date as DateType, datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User's email address",
        min_length=5,
        max_length=255
    )
    name: str = Field(
        ...,
        description="User's full name",
        min_length=1,
        max_length=100
    )
    password: str = Field(
        ...,
        description="User's password (minimum 6 characters)",
        min_length=6
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User's email address"
    )
    password: str = Field(
        ...,
        description="User's password"
    )


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="Refresh token to obtain new access token")


class UserResponse(BaseModel):
    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    role: str = Field(..., description="User's role in the household")
    household_id: Optional[UUID] = Field(None, description="Household ID if user belongs to one")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AccountCreate(BaseModel):
    name: str = Field(
        ...,
        description="Account name (e.g., 'My Savings', 'Cash Wallet')",
        min_length=1,
        max_length=100
    )
    type: str = Field(
        ...,
        description="Account type",
        pattern="^(cash|bank|wallet|digital_wallet|credit_card)$"
    )
    balance: Decimal = Field(
        default=Decimal("0"),
        description="Initial account balance (can be negative for credit cards)"
    )
    currency: str = Field(
        default="COP",
        description="Account currency code (ISO 4217)"
    )


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        description="Updated account name",
        min_length=1,
        max_length=100
    )
    type: Optional[str] = Field(
        None,
        description="Updated account type",
        pattern="^(cash|bank|wallet|digital_wallet|credit_card)$"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the account is active"
    )


class AccountResponse(BaseModel):
    id: UUID = Field(..., description="Account's unique identifier")
    household_id: UUID = Field(..., description="Household ID")
    name: str = Field(..., description="Account name")
    type: str = Field(..., description="Account type")
    balance: Decimal = Field(..., description="Current balance")
    currency: str = Field(default="COP", description="Currency code")
    is_active: bool = Field(..., description="Whether account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")


class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        description="Category name (e.g., 'Groceries', 'Salary')",
        min_length=1,
        max_length=50
    )
    type: str = Field(
        ...,
        description="Category type: 'income' or 'expense'",
        pattern="^(income|expense)$"
    )
    icon: Optional[str] = Field(
        None,
        description="Icon identifier for the category"
    )
    color: Optional[str] = Field(
        None,
        description="Hex color code for the category (e.g., '#FF5733')"
    )


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated category name", min_length=1, max_length=50)
    icon: Optional[str] = Field(None, description="Updated icon identifier")
    color: Optional[str] = Field(None, description="Updated hex color code")


class CategoryResponse(BaseModel):
    id: UUID = Field(..., description="Category's unique identifier")
    name: str = Field(..., description="Category name")
    type: str = Field(..., description="Category type")
    icon: Optional[str] = Field(None, description="Icon identifier")
    color: Optional[str] = Field(None, description="Hex color code")


class TransactionCreate(BaseModel):
    account_id: UUID = Field(..., description="Source account UUID")
    category_id: Optional[UUID] = Field(None, description="Category UUID for categorization")
    type: str = Field(
        default="expense",
        description="Transaction type: income, expense, or transfer (inferred from category if not provided)",
        pattern="^(income|expense|transfer)$"
    )
    amount: Decimal = Field(
        ...,
        description="Transaction amount (must be > 0)",
        gt=0
    )
    description: Optional[str] = Field(
        None,
        description="Optional transaction description"
    )
    date: DateType = Field(..., description="Transaction date (required)")
    to_account_id: Optional[UUID] = Field(
        None,
        description="Destination account UUID for transfers"
    )


class TransactionResponse(BaseModel):
    id: UUID = Field(..., description="Transaction's unique identifier")
    account_id: UUID = Field(..., description="Source account UUID")
    category_id: Optional[UUID] = Field(None, description="Category UUID")
    user_id: UUID = Field(..., description="User who created the transaction")
    type: str = Field(..., description="Transaction type")
    amount: Decimal = Field(..., description="Transaction amount")
    description: Optional[str] = Field(None, description="Transaction description")
    date: DateType = Field(..., description="Transaction date")
    to_account_id: Optional[UUID] = Field(None, description="Destination account UUID for transfers")
    created_at: datetime = Field(..., description="Transaction creation timestamp")


class BudgetCreate(BaseModel):
    category_id: UUID = Field(..., description="Category UUID for the budget")
    amount: Decimal = Field(
        ...,
        description="Budget amount (must be > 0)",
        gt=0
    )
    month: int = Field(
        ...,
        description="Budget month (1-12)",
        ge=1,
        le=12
    )
    year: int = Field(
        ...,
        description="Budget year (2020-2100)",
        ge=2020,
        le=2100
    )


class BudgetUpdate(BaseModel):
    amount: Decimal = Field(
        ...,
        description="Updated budget amount (must be > 0)",
        gt=0
    )


class BudgetResponse(BaseModel):
    id: UUID = Field(..., description="Budget's unique identifier")
    category_id: UUID = Field(..., description="Category UUID")
    household_id: UUID = Field(..., description="Household UUID")
    amount: Decimal = Field(..., description="Budget amount")
    month: int = Field(..., description="Budget month")
    year: int = Field(..., description="Budget year")


class DebtCreate(BaseModel):
    name: str = Field(
        ...,
        description="Debt name (e.g., 'Credit Card', 'Student Loan')",
        min_length=1,
        max_length=100
    )
    creditor: Optional[str] = Field(
        None,
        description="Creditor or lender name"
    )
    total_amount: Decimal = Field(
        ...,
        description="Total debt amount (must be > 0)",
        gt=0
    )
    current_balance: Decimal = Field(
        ...,
        description="Current outstanding balance (must be > 0)",
        gt=0
    )
    interest_rate: Decimal = Field(
        default=Decimal("0"),
        description="Annual interest rate percentage (must be >= 0)",
        ge=0
    )
    interest_rate_type: str = Field(
        default="EA",
        description="Interest rate type: EA (effective annual), EM (effective monthly), nominal (nominal annual), daily"
    )
    minimum_payment: Decimal = Field(
        default=Decimal("0"),
        description="Minimum monthly payment amount (must be >= 0)",
        ge=0
    )
    due_day: int = Field(
        default=1,
        description="Day of month when payment is due (1-31)",
        ge=1,
        le=31
    )
    start_date: Optional[DateType] = Field(None, description="Debt start date")
    end_date: Optional[DateType] = Field(None, description="Expected payoff date")


class DebtUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated debt name", min_length=1, max_length=100)
    creditor: Optional[str] = Field(None, description="Updated creditor name")
    current_balance: Optional[Decimal] = Field(None, description="Updated current balance", gt=0)
    interest_rate: Optional[Decimal] = Field(None, description="Updated interest rate", ge=0)
    interest_rate_type: Optional[str] = Field(None, description="Updated interest rate type")
    minimum_payment: Optional[Decimal] = Field(None, description="Updated minimum payment", ge=0)
    due_day: Optional[int] = Field(None, description="Updated payment due day", ge=1, le=31)
    status: Optional[str] = Field(None, description="Updated debt status")


class DebtResponse(BaseModel):
    id: UUID = Field(..., description="Debt's unique identifier")
    household_id: UUID = Field(..., description="Household UUID")
    name: str = Field(..., description="Debt name")
    creditor: Optional[str] = Field(None, description="Creditor name")
    total_amount: Decimal = Field(..., description="Total debt amount")
    current_balance: Decimal = Field(..., description="Current outstanding balance")
    interest_rate: Decimal = Field(..., description="Annual interest rate")
    interest_rate_type: str = Field(default="EA", description="Interest rate type")
    minimum_payment: Decimal = Field(..., description="Minimum monthly payment")
    due_day: int = Field(..., description="Payment due day")
    start_date: Optional[DateType] = Field(None, description="Debt start date")
    end_date: Optional[DateType] = Field(None, description="Expected payoff date")
    status: str = Field(..., description="Debt status")


class DebtPaymentCreate(BaseModel):
    amount: Decimal = Field(
        ...,
        description="Payment amount (must be > 0)",
        gt=0
    )
    payment_date: DateType = Field(..., description="Date of the payment")


class DebtPaymentResponse(BaseModel):
    id: UUID = Field(..., description="Payment's unique identifier")
    debt_id: UUID = Field(..., description="Associated debt UUID")
    amount: Decimal = Field(..., description="Payment amount")
    principal: Optional[Decimal] = Field(None, description="Principal portion of payment")
    interest: Optional[Decimal] = Field(None, description="Interest portion of payment")
    payment_date: DateType = Field(..., description="Payment date")
    is_reversed: bool = Field(False, description="Whether this payment has been reversed")


class MarkPaidRequest(BaseModel):
    year: int = Field(..., ge=2020, le=2050, description="Year to mark as paid")
    month: int = Field(..., ge=1, le=12, description="Month to mark as paid (1-12)")


class PaymentMonthHistory(BaseModel):
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month (1-12)")
    status: str = Field(..., description="Status: paid, pending, or reversed")
    payment_id: Optional[str] = Field(None, description="Payment ID if paid")
    amount: Optional[Decimal] = Field(None, description="Payment amount if paid")


class SavingsGoalCreate(BaseModel):
    name: str = Field(
        ...,
        description="Savings goal name (e.g., 'Vacation Fund', 'Emergency Fund')",
        min_length=1,
        max_length=100
    )
    target_amount: Decimal = Field(
        ...,
        description="Target savings amount (must be > 0)",
        gt=0
    )
    target_date: Optional[DateType] = Field(None, description="Target date to reach the goal")
    monthly_contribution: Optional[Decimal] = Field(
        None,
        description="Monthly contribution amount (auto-calculated if target_date is set, or used to calculate target_date)"
    )
    priority: str = Field(
        default="medium",
        description="Goal priority: 'low', 'medium', or 'high'"
    )
    goal_type: str = Field(
        default="savings",
        description="Goal type: 'savings' or 'investment'"
    )
    expected_return_rate: Optional[Decimal] = Field(
        None,
        description="Expected annual return rate for investments (e.g., 9.0 for 9% EA)",
        ge=0
    )
    horizon_months: Optional[int] = Field(
        None,
        description="Investment horizon in months",
        ge=1
    )


class SavingsGoalUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated goal name", min_length=1, max_length=100)
    target_amount: Optional[Decimal] = Field(None, description="Updated target amount", gt=0)
    target_date: Optional[DateType] = Field(None, description="Updated target date")
    monthly_contribution: Optional[Decimal] = Field(None, description="Updated monthly contribution")
    priority: Optional[str] = Field(None, description="Updated priority level")


class SavingsGoalResponse(BaseModel):
    id: UUID = Field(..., description="Savings goal's unique identifier")
    household_id: UUID = Field(..., description="Household UUID")
    name: str = Field(..., description="Goal name")
    target_amount: Decimal = Field(..., description="Target amount")
    current_amount: Decimal = Field(..., description="Current saved amount")
    target_date: Optional[DateType] = Field(None, description="Target date")
    monthly_contribution: Optional[Decimal] = Field(None, description="Monthly contribution amount")
    priority: str = Field(..., description="Priority level")
    goal_type: str = Field(default="savings", description="Goal type: savings or investment")
    expected_return_rate: Optional[Decimal] = Field(None, description="Expected annual return rate")
    horizon_months: Optional[int] = Field(None, description="Investment horizon in months")


class SavingsContributionCreate(BaseModel):
    amount: Decimal = Field(
        ...,
        description="Contribution amount (must be > 0)",
        gt=0
    )
    contribution_date: DateType = Field(..., description="Date of the contribution")


class SavingsContributionResponse(BaseModel):
    id: UUID = Field(..., description="Contribution's unique identifier")
    goal_id: UUID = Field(..., description="Associated savings goal UUID")
    amount: Decimal = Field(..., description="Contribution amount")
    contribution_date: DateType = Field(..., description="Contribution date")


class AssetCreate(BaseModel):
    name: str = Field(
        ...,
        description="Asset name (e.g., 'Car', 'Real Estate')",
        min_length=1,
        max_length=100
    )
    type: str = Field(
        ...,
        description="Asset type (e.g., 'vehicle', 'property', 'investment')",
        min_length=1,
        max_length=50
    )
    value: Decimal = Field(
        ...,
        description="Asset value (must be > 0)",
        gt=0
    )
    purchase_date: Optional[DateType] = Field(None, description="Date the asset was purchased")


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated asset name", min_length=1, max_length=100)
    type: Optional[str] = Field(None, description="Updated asset type", min_length=1, max_length=50)
    value: Optional[Decimal] = Field(None, description="Updated asset value", gt=0)
    purchase_date: Optional[DateType] = Field(None, description="Updated purchase date")


class AssetResponse(BaseModel):
    id: UUID = Field(..., description="Asset's unique identifier")
    household_id: UUID = Field(..., description="Household UUID")
    name: str = Field(..., description="Asset name")
    type: str = Field(..., description="Asset type")
    value: Decimal = Field(..., description="Asset value")
    purchase_date: Optional[DateType] = Field(None, description="Purchase date")


class LiabilityCreate(BaseModel):
    name: str = Field(
        ...,
        description="Liability name (e.g., 'Mortgage', 'Car Loan')",
        min_length=1,
        max_length=100
    )
    type: str = Field(
        ...,
        description="Liability type (e.g., 'mortgage', 'loan', 'credit')",
        min_length=1,
        max_length=50
    )
    total_amount: Decimal = Field(
        ...,
        description="Total liability amount (must be > 0)",
        gt=0
    )
    current_balance: Decimal = Field(
        ...,
        description="Current outstanding balance (must be > 0)",
        gt=0
    )
    interest_rate: Decimal = Field(
        default=Decimal("0"),
        description="Annual interest rate percentage (must be >= 0)",
        ge=0
    )
    interest_rate_type: str = Field(
        default="EA",
        description="Interest rate type: EA (effective annual), EM (effective monthly), nominal (nominal annual), daily"
    )
    monthly_payment: Decimal = Field(
        default=Decimal("0"),
        description="Monthly payment amount (must be >= 0)",
        ge=0
    )


class LiabilityUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated liability name", min_length=1, max_length=100)
    type: Optional[str] = Field(None, description="Updated liability type", min_length=1, max_length=50)
    current_balance: Optional[Decimal] = Field(None, description="Updated current balance", gt=0)
    interest_rate: Optional[Decimal] = Field(None, description="Updated interest rate", ge=0)
    interest_rate_type: Optional[str] = Field(None, description="Updated interest rate type")
    monthly_payment: Optional[Decimal] = Field(None, description="Updated monthly payment", ge=0)


class LiabilityResponse(BaseModel):
    id: UUID = Field(..., description="Liability's unique identifier")
    household_id: UUID = Field(..., description="Household UUID")
    name: str = Field(..., description="Liability name")
    type: str = Field(..., description="Liability type")
    total_amount: Decimal = Field(..., description="Total liability amount")
    current_balance: Decimal = Field(..., description="Current outstanding balance")
    interest_rate: Decimal = Field(..., description="Annual interest rate")
    interest_rate_type: str = Field(default="EA", description="Interest rate type")
    monthly_payment: Decimal = Field(..., description="Monthly payment amount")


class BudgetStatusItem(BaseModel):
    category: Optional[str] = Field(None, description="Category name")
    budgeted: Decimal = Field(..., description="Budgeted amount")
    spent: Decimal = Field(..., description="Amount spent")
    status: str = Field(..., description="Budget status: ok, warning, or over")
    message: Optional[str] = Field(None, description="Explanatory message")


class DashboardResponse(BaseModel):
    total_balance: Decimal = Field(..., description="Total balance across all accounts")
    monthly_income: Decimal = Field(..., description="Total income for current month")
    monthly_expenses: Decimal = Field(..., description="Total expenses for current month")
    net_monthly: Decimal = Field(..., description="Net income for current month")
    total_debt: Decimal = Field(..., description="Total outstanding debt")
    total_savings: Decimal = Field(..., description="Total savings across all goals")
    net_worth: Decimal = Field(..., description="Net worth (assets - liabilities)")
    recent_transactions: list[TransactionResponse] = Field(..., description="List of recent transactions")
    budget_status: list[BudgetStatusItem] = Field(..., description="Budget status for current month")
    upcoming_payments: list["RecurringPaymentResponse"] = Field(default=[], description="Upcoming recurring payments")
    savings_summary: Optional["SavingsSummary"] = Field(None, description="Savings goals summary")
    financial_alert: Optional[dict] = Field(None, description="Financial emergency alert")


class SavingsGoalSummary(BaseModel):
    name: str = Field(..., description="Goal name")
    current: Decimal = Field(..., description="Current amount saved")
    target: Decimal = Field(..., description="Target amount")
    target_date: Optional[DateType] = Field(None, description="Target date")


class SavingsSummary(BaseModel):
    total: Decimal = Field(..., description="Total savings")
    goals: list[SavingsGoalSummary] = Field(default=[], description="List of savings goals")


class RecurringPaymentCreate(BaseModel):
    account_id: Optional[UUID] = Field(None, description="Account to deduct from")
    category_id: Optional[UUID] = Field(None, description="Category for the payment")
    name: str = Field(..., description="Payment name (e.g., 'Netflix', 'Rent')", min_length=1, max_length=255)
    amount: Decimal = Field(..., description="Payment amount", gt=0)
    type: str = Field(default="expense", description="Payment type", pattern="^(expense|income)$")
    frequency: str = Field(default="monthly", description="Payment frequency", pattern="^(weekly|biweekly|monthly|yearly)$")
    day_of_month: int = Field(default=1, description="Day of month for monthly payments", ge=1, le=31)
    next_due_date: Optional[DateType] = Field(None, description="Next due date")
    description: Optional[str] = Field(None, description="Optional description")


class RecurringPaymentUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Payment name", min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, description="Payment amount", gt=0)
    type: Optional[str] = Field(None, description="Payment type", pattern="^(expense|income)$")
    frequency: Optional[str] = Field(None, description="Payment frequency", pattern="^(weekly|biweekly|monthly|yearly)$")
    day_of_month: Optional[int] = Field(None, description="Day of month", ge=1, le=31)
    next_due_date: Optional[DateType] = Field(None, description="Next due date")
    is_active: Optional[bool] = Field(None, description="Whether the payment is active")
    description: Optional[str] = Field(None, description="Optional description")


class RecurringPaymentResponse(BaseModel):
    id: UUID = Field(..., description="Recurring payment ID")
    household_id: UUID = Field(..., description="Household UUID")
    account_id: UUID = Field(..., description="Account UUID")
    category_id: Optional[UUID] = Field(None, description="Category UUID")
    name: str = Field(..., description="Payment name")
    amount: Decimal = Field(..., description="Payment amount")
    type: str = Field(..., description="Payment type")
    frequency: str = Field(..., description="Payment frequency")
    day_of_month: int = Field(..., description="Day of month")
    next_due_date: DateType = Field(..., description="Next due date")
    is_active: bool = Field(..., description="Whether active")
    description: Optional[str] = Field(None, description="Description")
    created_at: datetime = Field(..., description="Creation timestamp")


class CategoryAccountPreferenceCreate(BaseModel):
    category_id: UUID = Field(..., description="Category UUID")
    account_id: UUID = Field(..., description="Account UUID to use as default for this category")


class CategoryAccountPreferenceResponse(BaseModel):
    id: UUID = Field(..., description="Preference ID")
    household_id: UUID = Field(..., description="Household UUID")
    category_id: UUID = Field(..., description="Category UUID")
    account_id: UUID = Field(..., description="Default account UUID")


class GoalProjectionRequest(BaseModel):
    current_amount: Decimal = Field(..., description="Current amount saved", ge=0)
    monthly_contribution: Decimal = Field(..., description="Monthly contribution", gt=0)
    target_amount: Decimal = Field(..., description="Target amount", gt=0)
    expected_return_rate: Optional[Decimal] = Field(None, description="Annual return rate (e.g., 9 for 9% EA)", ge=0)
    horizon_months: Optional[int] = Field(None, description="Investment horizon in months", ge=1)


class GoalProjectionResponse(BaseModel):
    months_to_goal: Optional[int] = Field(None, description="Months needed to reach goal")
    projected_value: Decimal = Field(..., description="Projected value at horizon")
    total_contributions: Decimal = Field(..., description="Total amount contributed")
    total_interest: Decimal = Field(..., description="Total interest earned")
    monthly_breakdown: list[dict] = Field(default=[], description="Month-by-month projection")


class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    type: str = Field(
        ...,
        pattern="^(expense|payment|debt|income|goal)$",
        description="Event type",
    )
    amount: Decimal = Field(..., gt=0, description="Event amount (COP)")
    currency: str = Field(default="COP", description="Currency code")
    due_date: DateType = Field(..., description="Due date")
    recommended_date: Optional[DateType] = Field(None, description="Recommended payment date")
    cutoff_date: Optional[DateType] = Field(None, description="Cutoff date")
    account_id: Optional[UUID] = Field(None, description="Account UUID")
    responsible_member_id: Optional[UUID] = Field(None, description="Responsible member UUID")
    reminder_days_before: int = Field(default=3, description="Days before due to remind")
    notes: Optional[str] = Field(None, description="Notes")
    payment_method: Optional[str] = Field(
        None,
        pattern="^(card|cash|transfer)$",
        description="How the payment is made",
    )
    consequence_note: Optional[str] = Field(
        None,
        description="Consequence note (only if provided by user or obligation terms)",
    )
    category_id: Optional[UUID] = Field(None, description="Category UUID for expense categorization")
    visibility: str = Field(
        default="confirmed",
        pattern="^(confirmed|scheduled|estimated)$",
        description="How certain the event is",
    )
    confidence: int = Field(default=100, ge=0, le=100, description="System confidence 0-100")


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, pattern="^(expense|payment|debt|income|goal)$")
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = None
    due_date: Optional[DateType] = None
    recommended_date: Optional[DateType] = None
    cutoff_date: Optional[DateType] = None
    account_id: Optional[UUID] = None
    responsible_member_id: Optional[UUID] = None
    reminder_days_before: Optional[int] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = Field(None, pattern="^(card|cash|transfer)$")
    consequence_note: Optional[str] = None
    category_id: Optional[UUID] = None
    visibility: Optional[str] = Field(None, pattern="^(confirmed|scheduled|estimated)$")
    confidence: Optional[int] = Field(None, ge=0, le=100)


class EventResponse(BaseModel):
    id: UUID = Field(..., description="Event ID")
    household_id: UUID = Field(..., description="Household UUID")
    source: str = Field(..., description="Event source")
    source_id: Optional[UUID] = Field(None, description="Source entity ID")
    type: str = Field(..., description="Event type")
    title: str = Field(..., description="Event title")
    amount: Decimal = Field(..., description="Event amount")
    currency: str = Field(..., description="Currency")
    due_date: DateType = Field(..., description="Due date")
    recommended_date: Optional[DateType] = Field(None, description="Recommended date")
    cutoff_date: Optional[DateType] = Field(None, description="Cutoff date")
    status: str = Field(..., description="Event status")
    account_id: Optional[UUID] = Field(None, description="Account UUID")
    responsible_member_id: Optional[UUID] = Field(None, description="Responsible member UUID")
    is_recurrent: bool = Field(..., description="Whether recurrent")
    recurrence_group_id: Optional[UUID] = Field(None, description="Recurrence group ID")
    reminder_days_before: int = Field(..., description="Reminder days before")
    notes: Optional[str] = Field(None, description="Notes")
    confirmed: bool = Field(..., description="Confirmed flag")
    paid_at: Optional[datetime] = Field(None, description="Paid timestamp")
    paid_amount: Optional[Decimal] = Field(None, description="Paid amount")
    paid_by: Optional[UUID] = Field(None, description="Paid by user UUID")
    obligation_id: Optional[UUID] = Field(None, description="Obligation UUID")
    category_id: Optional[UUID] = Field(None, description="Category UUID for expense categorization")
    visibility: str = Field(..., description="Visibility")
    confidence: int = Field(..., description="Confidence")
    payment_method: Optional[str] = Field(None, description="Payment method")
    consequence_note: Optional[str] = Field(None, description="Consequence note")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class ObligationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Obligation name")
    type: str = Field(
        ...,
        pattern="^(expense|payment|debt|income|goal)$",
        description="Obligation type",
    )
    amount: Decimal = Field(..., gt=0, description="Obligation amount (COP)")
    currency: str = Field(default="COP", description="Currency code")
    frequency: str = Field(
        default="monthly",
        pattern="^(monthly|weekly|biweekly|yearly)$",
        description="Recurrence frequency",
    )
    anchor_day: Optional[int] = Field(None, ge=1, le=31, description="Day of month for due date")
    recommended_offset_days: int = Field(default=5, description="Days before due for recommended date")
    cutoff_offset_days: Optional[int] = Field(None, description="Days before due for cutoff date")
    reminder_days_before: int = Field(default=3, description="Days before due to remind")
    account_id: Optional[UUID] = Field(None, description="Account UUID")
    category_id: Optional[UUID] = Field(None, description="Category UUID")
    responsible_member_id: Optional[UUID] = Field(None, description="Responsible member UUID")
    is_active: bool = Field(default=True, description="Whether active")
    confidence: int = Field(default=100, ge=0, le=100, description="Confidence 0-100")
    notes: Optional[str] = Field(None, description="Notes")
    source: str = Field(default="USER", description="Obligation source")
    source_id: Optional[UUID] = Field(None, description="Source entity ID")
    generate_months: int = Field(default=12, ge=1, le=24, description="Months of events to generate")


class ObligationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, pattern="^(expense|payment|debt|income|goal)$")
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = None
    frequency: Optional[str] = Field(None, pattern="^(monthly|weekly|biweekly|yearly)$")
    anchor_day: Optional[int] = Field(None, ge=1, le=31)
    recommended_offset_days: Optional[int] = None
    cutoff_offset_days: Optional[int] = None
    reminder_days_before: Optional[int] = None
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    responsible_member_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    confidence: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class ObligationResponse(BaseModel):
    id: UUID = Field(..., description="Obligation ID")
    household_id: UUID = Field(..., description="Household UUID")
    source: str = Field(..., description="Obligation source")
    source_id: Optional[UUID] = Field(None, description="Source entity ID")
    name: str = Field(..., description="Obligation name")
    type: str = Field(..., description="Obligation type")
    amount: Decimal = Field(..., description="Obligation amount")
    currency: str = Field(..., description="Currency")
    frequency: str = Field(..., description="Frequency")
    anchor_day: Optional[int] = Field(None, description="Anchor day")
    recommended_offset_days: int = Field(..., description="Recommended offset days")
    cutoff_offset_days: Optional[int] = Field(None, description="Cutoff offset days")
    reminder_days_before: int = Field(..., description="Reminder days before")
    account_id: Optional[UUID] = Field(None, description="Account UUID")
    category_id: Optional[UUID] = Field(None, description="Category UUID")
    responsible_member_id: Optional[UUID] = Field(None, description="Responsible member UUID")
    is_active: bool = Field(..., description="Whether active")
    confidence: int = Field(..., description="Confidence")
    notes: Optional[str] = Field(None, description="Notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
