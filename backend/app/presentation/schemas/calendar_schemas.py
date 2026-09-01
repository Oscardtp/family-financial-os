from pydantic import BaseModel, Field
from datetime import date as DateType, datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional


class CalendarEventCreate(BaseModel):
    title: str = Field(..., description="Event title", min_length=1, max_length=255)
    type: str = Field(default="expense", description="Event type", pattern="^(income|expense|payment|goal_contribution)$")
    amount: Decimal = Field(..., description="Event amount", gt=0)
    due_date: DateType = Field(..., description="Due date")
    recommended_date: Optional[DateType] = Field(None, description="Recommended payment date")
    cutoff_date: Optional[DateType] = Field(None, description="Cutoff date")
    account_id: Optional[str] = Field(None, description="Account UUID")
    responsible_member_id: Optional[str] = Field(None, description="Responsible member UUID")
    notes: Optional[str] = Field(None, description="Additional notes")
    confirmed: bool = Field(default=True, description="Whether event is confirmed")


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, pattern="^(income|expense|payment|goal_contribution)$")
    amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[DateType] = None
    recommended_date: Optional[DateType] = None
    cutoff_date: Optional[DateType] = None
    account_id: Optional[str] = None
    responsible_member_id: Optional[str] = None
    notes: Optional[str] = None
    confirmed: Optional[bool] = None


class CalendarEventResponse(BaseModel):
    id: UUID
    household_id: UUID
    source: str
    source_id: Optional[str] = None
    type: str
    title: str
    amount: Decimal
    currency: str = "COP"
    due_date: DateType
    recommended_date: Optional[DateType] = None
    cutoff_date: Optional[DateType] = None
    status: str
    account_id: Optional[str] = None
    responsible_member_id: Optional[str] = None
    is_recurrent: bool = False
    recurrence_group_id: Optional[str] = None
    reminder_days_before: int = 3
    notes: Optional[str] = None
    confirmed: bool = True
    paid_at: Optional[datetime] = None
    paid_amount: Optional[Decimal] = None
    paid_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CalendarMonthResponse(BaseModel):
    year: int
    month: int
    events: list[CalendarEventResponse]
    summary: dict


class CalendarProjectionResponse(BaseModel):
    available_balance: float
    pending_payments: float
    expected_income: float
    projected_balance: float
    events_7_days: list[dict]
    events_30_days_count: int


class CalendarSyncResponse(BaseModel):
    created: int
    skipped: int


class MarkPaidRequest(BaseModel):
    amount: Optional[float] = Field(None, description="Payment amount (defaults to event amount)")


class PatternSuggestionResponse(BaseModel):
    title: str
    avg_amount: float
    avg_day: int
    occurrences: int
    source: str
    source_id: Optional[str] = None
