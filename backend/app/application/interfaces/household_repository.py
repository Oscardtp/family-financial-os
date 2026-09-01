from abc import ABC, abstractmethod
from typing import Optional
import uuid


class HouseholdRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def create(self, household: dict) -> dict:
        ...

    @abstractmethod
    async def add_member(self, household_id: uuid.UUID, user_id: uuid.UUID, role: str = "member") -> dict:
        ...
