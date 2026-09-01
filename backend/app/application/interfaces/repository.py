from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
import uuid

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        ...

    @abstractmethod
    async def get_all(self, household_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[T]:
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        ...

    @abstractmethod
    async def update(self, entity: T) -> T:
        ...

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        ...
