from abc import ABC, abstractmethod
from typing import Optional
import uuid


class BudgetRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(self, household_id: uuid.UUID, month: int, year: int) -> list[dict]:
        ...

    @abstractmethod
    async def get_by_category_and_period(
        self, household_id: uuid.UUID, category_id: uuid.UUID, month: int, year: int
    ) -> Optional[dict]:
        ...

    @abstractmethod
    async def create(self, budget: dict) -> dict:
        ...

    @abstractmethod
    async def update(self, budget: dict) -> dict:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...
