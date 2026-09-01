from abc import ABC, abstractmethod
from typing import Optional
import uuid


class FinancialObligationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(self, household_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict]:
        ...

    @abstractmethod
    async def get_active(self, household_id: uuid.UUID) -> list[dict]:
        ...

    @abstractmethod
    async def get_by_source(self, household_id: uuid.UUID, source: str, source_id: str) -> Optional[dict]:
        ...

    @abstractmethod
    async def create(self, obligation: dict) -> dict:
        ...

    @abstractmethod
    async def update(self, obligation: dict) -> dict:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...
