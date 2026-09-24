import json
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.budget_method import list_presets, get_preset
from app.domain.value_objects.money import Money
from app.financial_engine.budget_engine import BudgetEngine
from app.infrastructure.models.models import HouseholdBudgetMethodModel


def _parse_json(raw, default):
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return default


class BudgetMethodService:
    """FASE 6.3B — Household method configuration.

    Persists ONLY the method configuration row. Never reads, creates,
    updates or deletes Budget rows.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def presets(self) -> list:
        return list_presets()

    async def get_config(self, household_id: str) -> dict:
        row = await self.db.get(HouseholdBudgetMethodModel, household_id)
        if row is None:
            return {
                "method_type": None,
                "groups": [],
                "category_groups": {},
                "reference_income_source": "manual",
                "reference_income_amount": None,
                "updated_at": None,
            }
        return {
            "method_type": row.method_type,
            "groups": _parse_json(row.groups_json, []),
            "category_groups": _parse_json(row.category_groups_json, {}),
            "reference_income_source": row.reference_income_source or "manual",
            "reference_income_amount": (
                Decimal(str(row.reference_income_amount))
                if row.reference_income_amount is not None
                else None
            ),
            "updated_at": row.updated_at,
        }

    async def save_config(self, household_id: str, data) -> dict:
        """Upsert the household method row. Budgets table is never touched."""
        method_type = data.method_type
        if method_type is not None and method_type != "custom" and get_preset(method_type) is None:
            raise ValueError(f"Método desconocido: {method_type}")

        groups = [
            {"key": g.key, "label": g.label, "pct": g.pct}
            for g in (data.groups or [])
        ]
        category_groups = dict(data.category_groups or {})
        valid_keys = {g["key"] for g in groups}
        category_groups = {
            cat_id: key for cat_id, key in category_groups.items() if key in valid_keys
        }

        row = await self.db.get(HouseholdBudgetMethodModel, household_id)
        if row is None:
            row = HouseholdBudgetMethodModel(household_id=household_id)
            self.db.add(row)
        row.method_type = method_type
        row.groups_json = json.dumps(groups)
        row.category_groups_json = json.dumps(category_groups)
        row.reference_income_source = data.reference_income_source
        row.reference_income_amount = data.reference_income_amount
        await self.db.flush()
        return await self.get_config(household_id)

    def preview(self, income_amount: Decimal, groups: list) -> dict:
        """Compute a distribution preview. Pure calculation, no persistence."""
        engine = BudgetEngine()
        result = engine.distribute_by_groups(
            Money(income_amount),
            [{"key": g.key, "pct": g.pct} for g in groups],
        )
        allocations = [
            {
                "key": g.key,
                "label": g.label,
                "pct": g.pct,
                "amount": result[g.key].amount,
            }
            for g in groups
        ]
        return {"income_amount": Decimal(income_amount), "allocations": allocations}
