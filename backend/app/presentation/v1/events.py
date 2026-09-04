import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member
from app.presentation.schemas.schemas import (
    EventCreate, EventUpdate, EventResponse,
)
from app.application.services.event_service import FinancialEventService
from app.application.services.calendar_service import CalendarService
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.financial_event_repository import SQLAlchemyFinancialEventRepository
from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.application.interfaces.transaction_repository import TransactionRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["Financial Events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    year: int | None = Query(None, description="Year for month view"),
    month: int | None = Query(None, description="Month (1-12) for month view"),
    from_date: date | None = Query(None, description="Range start (inclusive)"),
    to_date: date | None = Query(None, description="Range end (exclusive)"),
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    if year and month:
        return await service.get_month(current_user["household_id"], year, month)
    if from_date and to_date:
        return await service.get_range(current_user["household_id"], from_date, to_date)
    return await service.get_month(current_user["household_id"], date.today().year, date.today().month)


@router.get("/upcoming", response_model=list[EventResponse])
async def upcoming_events(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    return await service.get_upcoming(current_user["household_id"], days)


@router.get("/availability")
async def availability(
    days: int = Query(7, ge=1, le=365),
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = CalendarService(
        db,
        account_repo=SQLAlchemyAccountRepository(db),
        event_repo=SQLAlchemyFinancialEventRepository(db),
        budget_repo=SQLAlchemyBudgetRepository(db),
        tx_repo=SQLAlchemyTransactionRepository(db),
    )
    return await service.availability(current_user["household_id"], days)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    try:
        return await service.get(event_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este evento")


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    data: EventCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    result = await service.create(data, current_user["household_id"], current_user["id"])
    await db.commit()
    return result


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    data: EventUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    try:
        result = await service.update(event_id, data, current_user["household_id"])
        await db.commit()
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este evento")


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    try:
        await service.delete(event_id, current_user["household_id"])
        await db.commit()
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este evento")


@router.post("/{event_id}/pay", response_model=EventResponse)
async def mark_paid(
    event_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    try:
        result = await service.mark_as_paid(event_id, current_user)
        await db.commit()
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este evento")


@router.post("/{event_id}/unpay", response_model=EventResponse)
async def unpay(
    event_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialEventService(db)
    try:
        result = await service.unpay(event_id, current_user)
        await db.commit()
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este evento")
    except Exception:
        logger.exception("Error inesperado en unpay para evento %s", event_id)
        raise HTTPException(status_code=500, detail="No pudimos anular el pago. Intenta de nuevo.")
