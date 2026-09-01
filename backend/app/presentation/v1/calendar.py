from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.presentation.deps import get_current_user, require_member
from app.application.services.calendar_service import CalendarService
from app.presentation.schemas.calendar_schemas import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
    CalendarMonthResponse,
    CalendarProjectionResponse,
    CalendarSyncResponse,
    MarkPaidRequest,
    PatternSuggestionResponse,
)

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/events", response_model=list[CalendarEventResponse])
async def get_events(
    year: int = None,
    month: int = None,
    date_from: str = None,
    date_to: str = None,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    if year and month:
        events = await service.get_month_events(user["household_id"], year, month)
    elif date_from and date_to:
        events = await service.get_date_range_events(
            user["household_id"],
            date.fromisoformat(date_from),
            date.fromisoformat(date_to),
        )
    else:
        today = date.today()
        events = await service.get_month_events(user["household_id"], today.year, today.month)
    return events


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    event = await service.get_event(user["household_id"], event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events", response_model=CalendarEventResponse)
async def create_event(
    data: CalendarEventCreate,
    user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    event = await service.create_manual_event(user["household_id"], data.model_dump())
    return event


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    data: CalendarEventUpdate,
    user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    event = await service.update_event(user["household_id"], event_id, update_data)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not editable")
    return event


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    deleted = await service.delete_event(user["household_id"], event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found or not deletable")
    return {"detail": "Event deleted"}


@router.post("/events/{event_id}/pay", response_model=CalendarEventResponse)
async def mark_event_paid(
    event_id: str,
    data: MarkPaidRequest = MarkPaidRequest(),
    user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    event = await service.mark_as_paid(
        user["household_id"],
        event_id,
        user["id"],
        data.amount,
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/sync", response_model=CalendarSyncResponse)
async def sync_events(
    user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    result = await service.sync_events(user["household_id"])
    return result


@router.get("/projection", response_model=CalendarProjectionResponse)
async def get_projection(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    return await service.get_projection(user["household_id"])


@router.get("/summary")
async def get_summary(
    year: int = None,
    month: int = None,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    today = date.today()
    y = year or today.year
    m = month or today.month
    return await service.get_summary(user["household_id"], y, m)


@router.get("/patterns", response_model=list[PatternSuggestionResponse])
async def get_patterns(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(db)
    return await service.detect_patterns(user["household_id"])
