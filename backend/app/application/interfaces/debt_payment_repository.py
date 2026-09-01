from abc import ABC, abstractmethod
from typing import Optional
import uuid


class DebtPaymentRepository(ABC):
    @abstractmethod
    async def get_by_debt_id(self, debt_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict]:
        ...

    @abstractmethod
    async def get_by_id(self, payment_id: str) -> Optional[dict]:
        ...

    @abstractmethod
    async def create(self, payment: dict) -> dict:
        ...

    @abstractmethod
    async def reverse(self, payment_id: str) -> None:
        ...
