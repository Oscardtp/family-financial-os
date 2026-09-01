from abc import ABC, abstractmethod
from typing import Optional
import uuid


class DebtPaymentOverrideRepository(ABC):
    @abstractmethod
    async def get_by_debt_and_month(self, debt_id: str, year: int, month: int) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_by_debt_id(self, debt_id: str) -> list[dict]:
        ...

    @abstractmethod
    async def create(self, override: dict) -> dict:
        ...
