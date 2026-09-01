from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from decimal import Decimal
from app.database import get_db
from app.presentation.deps import require_viewer, require_member
from app.presentation.schemas.schemas import (
    ObligationCreate, ObligationUpdate, ObligationResponse,
)
from app.application.services.obligation_service import FinancialObligationService
from app.application.services.event_service import FinancialEventService
from app.application.services.obligation_sync_service import ObligationSyncService
from app.infrastructure.repositories.debt_repository import SQLAlchemyDebtRepository

router = APIRouter(prefix="/obligations", tags=["Financial Obligations"])


@router.get("", response_model=list[ObligationResponse])
async def list_obligations(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialObligationService(db)
    return await service.list(current_user["household_id"])


@router.post("", response_model=ObligationResponse, status_code=201)
async def create_obligation(
    data: ObligationCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialObligationService(db)
    result = await service.create(data, current_user["household_id"], current_user["id"])
    await db.commit()
    return result


@router.post("/sync-existing-debts", status_code=201)
async def sync_existing_debts(
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    debt_repo = SQLAlchemyDebtRepository(db)
    debts = await debt_repo.get_all(current_user["household_id"])
    active_debts = [d for d in debts if d.get("status") == "active"]

    sync = ObligationSyncService(db)
    synced = 0
    for debt in active_debts:
        obligation = await sync.obligation_repo.get_by_source(
            current_user["household_id"], "SYSTEM", str(debt["id"])
        )
        if not obligation:
            await sync.sync_debt(debt, current_user["household_id"])
            synced += 1

    await db.commit()
    return {"synced": synced, "total_active": len(active_debts)}


@router.post("/from-event", response_model=ObligationResponse, status_code=201)
async def create_obligation_from_event(
    payload: dict = Body(...),
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    event_id = payload.get("event_id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Se requiere event_id")
    event_service = FinancialEventService(db)
    obligation_service = FinancialObligationService(db)

    event = await event_service.get(event_id, current_user["household_id"])
    due = event.get("due_date")
    recommended = event.get("recommended_date")
    cutoff = event.get("cutoff_date")

    def _to_date(d):
        if hasattr(d, "day"):
            return d
        if isinstance(d, str):
            return date.fromisoformat(d)
        return None

    due_date = _to_date(due)
    recommended_date = _to_date(recommended)
    cutoff_date = _to_date(cutoff)

    anchor_day = due_date.day if due_date else 1
    recommended_offset = 0
    cutoff_offset = None
    if recommended_date and due_date:
        recommended_offset = max((due_date - recommended_date).days, 0)
    if cutoff_date and due_date:
        cutoff_offset = max((due_date - cutoff_date).days, 0)

    obligation_data = {
        "household_id": current_user["household_id"],
        "source": "USER",
        "source_id": event_id,
        "name": event.get("title", ""),
        "type": event.get("type", "expense"),
        "amount": Decimal(str(event.get("amount") or 0)),
        "currency": event.get("currency", "COP"),
        "frequency": "monthly",
        "anchor_day": anchor_day,
        "recommended_offset_days": recommended_offset,
        "cutoff_offset_days": cutoff_offset,
        "reminder_days_before": event.get("reminder_days_before", 3),
        "account_id": event.get("account_id"),
        "category_id": None,
        "responsible_member_id": event.get("responsible_member_id"),
        "is_active": True,
        "confidence": event.get("confidence", 100),
        "notes": event.get("notes"),
    }
    obligation = await obligation_service.repo.create(obligation_data)
    await obligation_service.event_repo.delete_upcoming_by_obligation(
        current_user["household_id"], obligation["id"], date.today()
    )
    full_obligation = await obligation_service.repo.get_by_id(obligation["id"])
    if full_obligation and full_obligation.get("amount") and full_obligation["amount"] > 0:
        from app.application.services.obligation_service import generate_events_for_obligation
        await generate_events_for_obligation(obligation_service.event_repo, full_obligation, 12)

    await db.commit()
    return full_obligation


@router.get("/{obligation_id}", response_model=ObligationResponse)
async def get_obligation(
    obligation_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialObligationService(db)
    try:
        return await service.get(obligation_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta obligación")


@router.put("/{obligation_id}", response_model=ObligationResponse)
async def update_obligation(
    obligation_id: str,
    data: ObligationUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialObligationService(db)
    try:
        result = await service.update(obligation_id, data, current_user["household_id"])
        await db.commit()
        return result
    except ValueError:
       raise HTTPException(status_code=404, detail="No encontramos esta obligación")


@router.delete("/{obligation_id}", status_code=204)
async def delete_obligation(
    obligation_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialObligationService(db)
    try:
        await service.delete(obligation_id, current_user["household_id"])
        await db.commit()
    except ValueError:
       raise HTTPException(status_code=404, detail="No encontramos esta obligación")
