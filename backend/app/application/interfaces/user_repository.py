from abc import ABC, abstractmethod
from typing import Optional
import uuid


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[dict]:
        ...

    @abstractmethod
    async def create(self, user: dict) -> dict:
        ...

    @abstractmethod
    async def update(self, user: dict) -> dict:
        ...
