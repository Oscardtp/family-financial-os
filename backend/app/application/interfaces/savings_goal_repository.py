from abc import ABC, abstractmethod
from typing import Optional
import uuid


class SavingsGoalRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(self, household_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict]:
        ...

    @abstractmethod
    async def create(self, goal: dict) -> dict:
        ...

    @abstractmethod
    async def update(self, goal: dict) -> dict:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...
