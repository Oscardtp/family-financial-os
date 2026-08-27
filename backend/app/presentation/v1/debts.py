from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.presentation.schemas.schemas import (
    DebtCreate, DebtUpdate, DebtResponse,
    DebtPaymentCreate, DebtPaymentResponse,
    MarkPaidRequest, PaymentMonthHistory,
)
from app.application.services.debt_service import DebtService

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.get("", response_model=list[DebtResponse], summary="List debts", description="Returns all debts with payment history")
async def list_debts(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    return await service.list(current_user["household_id"], skip, limit)


@router.get("/due-alerts", summary="Due date alerts", description="Get alerts for debts with upcoming or overdue payments")
async def get_due_alerts(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    return await service.get_due_alerts(current_user["household_id"])


@router.post("", response_model=DebtResponse, status_code=201, summary="Create debt", description="Register a new debt (credit card, loan, etc.)")
async def create_debt(
    data: DebtCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    return await service.create(data, current_user["household_id"])


@router.get("/{debt_id}", response_model=DebtResponse, summary="Get debt details", description="Returns full details of a specific debt")
async def get_debt(
    debt_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.get(debt_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta deuda")


@router.put("/{debt_id}", response_model=DebtResponse, summary="Update debt", description="Modify debt details")
async def update_debt(
    debt_id: str,
    data: DebtUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.update(debt_id, data, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta deuda")


@router.delete("/{debt_id}", status_code=204, summary="Delete debt", description="Remove a debt record")
async def delete_debt(
    debt_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        await service.delete(debt_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta deuda")


@router.post("/{debt_id}/payments", response_model=DebtPaymentResponse, status_code=201, summary="Record debt payment", description="Add a payment toward a debt")
async def create_debt_payment(
    debt_id: str,
    data: DebtPaymentCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.create_payment(debt_id, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{debt_id}/payments/{payment_id}", status_code=204, summary="Reverse debt payment", description="Reverse a previously recorded payment and restore the balance")
async def reverse_debt_payment(
    debt_id: str,
    payment_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        await service.reverse_payment(debt_id, payment_id, current_user["household_id"])
    except ValueError as e:
        detail = str(e)
        status = 400 if "already reversed" in detail else 404
        raise HTTPException(status_code=status, detail=detail)


@router.post("/{debt_id}/toggle", response_model=DebtResponse, summary="Toggle debt status", description="Toggle between active and paused status")
async def toggle_debt_status(
    debt_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.toggle_status(debt_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{debt_id}/payments", response_model=list[DebtPaymentResponse], summary="List debt payments", description="Returns all payments made toward a specific debt")
async def list_debt_payments(
    debt_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.list_payments(debt_id, current_user["household_id"], skip, limit)
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta deuda")


@router.post("/{debt_id}/mark-paid", status_code=201, summary="Mark historical month as paid", description="Mark a past month as paid without recording a real payment")
async def mark_month_paid(
    debt_id: str,
    data: MarkPaidRequest,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.mark_month_paid(debt_id, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{debt_id}/payment-history", response_model=list[PaymentMonthHistory], summary="Payment history calendar", description="Returns monthly payment status for a debt since its start date")
async def get_payment_history(
    debt_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.get_payment_history(debt_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta deuda")


@router.get("/{debt_id}/amortization", summary="Amortization schedule", description="Generate full amortization schedule for a debt")
async def get_amortization_schedule(
    debt_id: str,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    try:
        return await service.get_amortization(debt_id, current_user["household_id"])
    except ValueError:
        raise HTTPException(status_code=404, detail="No encontramos esta deuda")
