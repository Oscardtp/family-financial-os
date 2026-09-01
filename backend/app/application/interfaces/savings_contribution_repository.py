from abc import ABC, abstractmethod
import uuid


class SavingsContributionRepository(ABC):
    @abstractmethod
    async def get_by_goal_id(self, goal_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict]:
        ...

    @abstractmethod
    async def create(self, contribution: dict) -> dict:
        ...
