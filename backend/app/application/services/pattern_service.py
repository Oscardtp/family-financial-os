from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.pattern_repository import SQLAlchemyDetectedPatternRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository


class PatternService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pattern_repo = SQLAlchemyDetectedPatternRepository(db)
        self.tx_repo = SQLAlchemyTransactionRepository(db)
        self.category_repo = SQLAlchemyCategoryRepository(db)

    async def detect_patterns(self, household_id: str) -> list[dict]:
        transactions = await self.tx_repo.get_all(household_id, limit=500)
        if len(transactions) < 3:
            return []

        grouped = {}
        for tx in transactions:
            key = (tx.get("description") or "sin descripcion", tx["type"])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(tx)

        patterns = []
        for (desc_key, tx_type), txs in grouped.items():
            if len(txs) < 2:
                continue

            amounts = [Decimal(str(tx["amount"])) for tx in txs]
            avg_amount = sum(amounts) / len(amounts)

            days = [tx["date"].day for tx in txs if hasattr(tx["date"], "day")]
            avg_day = round(sum(days) / len(days)) if days else None

            amounts_var = sum((a - avg_amount) ** 2 for a in amounts) / len(amounts)
            amounts_std = amounts_var ** Decimal("0.5")
            coeff_var = (amounts_std / avg_amount * 100) if avg_amount > 0 else 100

            if coeff_var > 15:
                continue

            frequency = self._detect_frequency(txs)
            confidence = min(95, 50 + len(txs) * 5)

            existing = await self.pattern_repo.find_existing(
                household_id, desc_key, tx_type
            )

            pattern_data = {
                "household_id": household_id,
                "name": desc_key,
                "type": tx_type,
                "avg_amount": avg_amount.quantize(Decimal("0.01")),
                "avg_day_of_month": avg_day,
                "frequency": frequency,
                "occurrences": len(txs),
                "confidence": confidence,
                "source": "transaction",
                "first_seen": min(tx["date"] for tx in txs),
                "last_seen": max(tx["date"] for tx in txs),
            }

            if existing:
                pattern_data["occurrences"] = max(existing["occurrences"], len(txs))
                pattern_data["confidence"] = min(95, existing["confidence"] + 5)

            patterns.append(pattern_data)

        return patterns

    async def persist_patterns(self, household_id: str) -> list[dict]:
        patterns = await self.detect_patterns(household_id)
        persisted = []
        for pattern in patterns:
            existing = await self.pattern_repo.find_existing(
                household_id, pattern["name"], pattern["type"]
            )
            if existing:
                result = await self.pattern_repo.update(
                    existing["id"], {
                        "avg_amount": pattern["avg_amount"],
                        "occurrences": pattern["occurrences"],
                        "confidence": pattern["confidence"],
                        "last_seen": pattern["last_seen"],
                    }
                )
            else:
                result = await self.pattern_repo.create(pattern)
            persisted.append(result)
        return persisted

    async def get_patterns(self, household_id: str) -> list[dict]:
        return await self.pattern_repo.get_by_household(household_id)

    async def get_unconfirmed(self, household_id: str) -> list[dict]:
        return await self.pattern_repo.get_unconfirmed(household_id)

    async def confirm_pattern(self, pattern_id: str) -> dict | None:
        return await self.pattern_repo.confirm(pattern_id)

    async def reject_pattern(self, pattern_id: str) -> dict | None:
        return await self.pattern_repo.reject(pattern_id)

    def _detect_frequency(self, transactions: list[dict]) -> str:
        if len(transactions) < 2:
            return "monthly"

        dates = sorted(tx["date"] for tx in transactions)
        gaps = []
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i - 1]).days
            gaps.append(gap)

        avg_gap = sum(gaps) / len(gaps) if gaps else 30

        if avg_gap <= 8:
            return "weekly"
        elif avg_gap <= 16:
            return "biweekly"
        else:
            return "monthly"
