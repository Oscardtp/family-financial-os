from abc import ABC, abstractmethod
from typing import Optional
import uuid


class CategoryAccountPreferenceRepository(ABC):
    @abstractmethod
    async def get_by_category(self, household_id: uuid.UUID, category_id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(self, household_id: uuid.UUID) -> list[dict]:
        ...

    @abstractmethod
    async def create_or_update(self, preference: dict) -> dict:
        ...

    @abstractmethod
    async def delete(self, household_id: uuid.UUID, category_id: uuid.UUID) -> bool:
        ...
