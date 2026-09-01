from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
import uuid


class TransactionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(
        self,
        household_id: uuid.UUID,
        account_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        ...

    @abstractmethod
    async def create(self, transaction: dict) -> dict:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...

    @abstractmethod
    async def get_totals_by_category(
        self, household_id: uuid.UUID, date_from: date, date_to: date
    ) -> list[dict]:
        ...

    @abstractmethod
    async def get_monthly_totals(
        self, household_id: uuid.UUID, year: int, month: int
    ) -> dict:
        ...
