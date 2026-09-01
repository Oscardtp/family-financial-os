from abc import ABC, abstractmethod
from typing import Optional
import uuid


class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(self, household_id: uuid.UUID) -> list[dict]:
        ...

    @abstractmethod
    async def create(self, category: dict) -> dict:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...
