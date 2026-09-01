from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
import uuid


class FinancialEventRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(self, household_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict]:
        ...

    @abstractmethod
    async def get_by_month(self, household_id: uuid.UUID, year: int, month: int) -> list[dict]:
        ...

    @abstractmethod
    async def get_by_date_range(self, household_id: uuid.UUID, date_from: date, date_to: date) -> list[dict]:
        ...

    @abstractmethod
    async def get_pending(self, household_id: uuid.UUID) -> list[dict]:
        ...

    @abstractmethod
    async def get_overdue(self, household_id: uuid.UUID, as_of: date) -> list[dict]:
        ...

    @abstractmethod
    async def get_upcoming(self, household_id: uuid.UUID, as_of: date, days: int = 30) -> list[dict]:
        ...

    @abstractmethod
    async def create(self, event: dict) -> dict:
        ...

    @abstractmethod
    async def update(self, event: dict) -> dict:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...

    @abstractmethod
    async def mark_as_paid(self, id: uuid.UUID, paid_by: str, paid_amount: float, paid_at) -> dict:
        ...

    @abstractmethod
    async def exists_for_source(self, household_id: uuid.UUID, source: str, source_id: str, due_date: date) -> bool:
        ...

    @abstractmethod
    async def get_by_recurrence_group(self, household_id: uuid.UUID, recurrence_group_id: str) -> list[dict]:
        ...

    @abstractmethod
    async def delete_upcoming_by_obligation(self, household_id: uuid.UUID, obligation_id: str, as_of: date) -> int:
        ...
