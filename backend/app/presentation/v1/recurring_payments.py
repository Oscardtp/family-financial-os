from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member
from app.presentation.schemas.schemas import (
    RecurringPaymentCreate, RecurringPaymentUpdate, RecurringPaymentResponse,
)
from app.application.services.recurring_payment_service import RecurringPaymentService

router = APIRouter(prefix="/recurring-payments", tags=["Recurring Payments"])


@router.get("", response_model=list[RecurringPaymentResponse])
async def list_recurring_payments(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = RecurringPaymentService(db)
    return await service.list(current_user["household_id"], skip, limit)


@router.post("", response_model=RecurringPaymentResponse, status_code=201)
async def create_recurring_payment(
    data: RecurringPaymentCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = RecurringPaymentService(db)
    result = await service.create(data, current_user["household_id"], current_user["id"])
    await db.commit()
    return result


@router.get("/{payment_id}", response_model=RecurringPaymentResponse)
async def get_recurring_payment(
    payment_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = RecurringPaymentService(db)
    try:
        return await service.get(payment_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este pago recurrente")


@router.put("/{payment_id}", response_model=RecurringPaymentResponse)
async def update_recurring_payment(
    payment_id: str,
    data: RecurringPaymentUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = RecurringPaymentService(db)
    try:
        result = await service.update(payment_id, data, current_user["household_id"])
        await db.commit()
        return result
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este pago recurrente")


@router.delete("/{payment_id}", status_code=204)
async def delete_recurring_payment(
    payment_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = RecurringPaymentService(db)
    try:
        await service.delete(payment_id, current_user["household_id"])
        await db.commit()
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos este pago recurrente")


@router.post("/{payment_id}/pay", response_model=RecurringPaymentResponse)
async def mark_as_paid(
    payment_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = RecurringPaymentService(db)
    try:
        result = await service.pay(payment_id, current_user)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/process-due")
async def process_due_payments(
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = RecurringPaymentService(db)
    result = await service.process_due(current_user["household_id"], current_user["id"])
    await db.commit()
    return result
