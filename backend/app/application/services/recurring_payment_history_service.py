from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository


class RecurringPaymentHistoryService:
    def __init__(self, db):
        self.tx_repo = SQLAlchemyTransactionRepository(db)

    async def get_payments(self, payment_id: str, household_id: str, skip: int = 0, limit: int = 100) -> list[dict]:
        return await self.tx_repo.get_by_recurring(payment_id, household_id, skip, limit)
