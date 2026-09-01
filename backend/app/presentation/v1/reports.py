from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import csv
import io
from app.database import get_db
from app.presentation.deps import get_current_user
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/transactions/csv", summary="Export transactions CSV", description="Download all transactions as a CSV file with optional date filters")
async def export_transactions_csv(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyTransactionRepository(db)
    transactions = await repo.get_all(
        current_user["household_id"],
        date_from=start_date,
        date_to=end_date,
        limit=10000,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Tipo", "Monto", "Descripcion", "Cuenta", "Categoria"])

    for tx in transactions:
        writer.writerow([
            tx["date"],
            tx["type"],
            tx["amount"],
            tx.get("description", ""),
            tx.get("account_id", ""),
            tx.get("category_id", ""),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=transacciones_{date.today().isoformat()}.csv"},
    )
