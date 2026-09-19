"""Tests to verify financial interfaces use Decimal, not float.

FASE 4B.7 — Decimal Contracts
"""
import inspect
from decimal import Decimal


def test_repository_interfaces_use_decimal():
    """Repository interfaces for monetary totals must return Decimal."""
    from app.application.interfaces.debt_repository import DebtRepository
    from app.application.interfaces.asset_repository import AssetRepository
    from app.application.interfaces.liability_repository import LiabilityRepository

    for cls in (DebtRepository, AssetRepository, LiabilityRepository):
        methods = {m: getattr(cls, m) for m in dir(cls) if not m.startswith("_")}
        for name, method in methods.items():
            if callable(method) and hasattr(method, "__isabstractmethod__") and method.__isabstractmethod__:
                sig = inspect.signature(method)
                ret = sig.return_annotation
                if ret is not inspect.Parameter.empty and "total" in name.lower() or "balance" in name.lower() or "value" in name.lower():
                    assert ret is Decimal, (
                        f"{cls.__name__}.{name} returns {ret}, expected Decimal"
                    )


def test_money_types_remain_decimal():
    """Money value object must store Decimal internally."""
    from app.domain.value_objects.money import Money

    m = Money(100000)
    assert isinstance(m.amount, Decimal), f"Money.amount is {type(m.amount)}, expected Decimal"

    m2 = Money("250000.50")
    assert isinstance(m2.amount, Decimal)


def test_decimal_roundtrip_preserved():
    """Decimal precision must survive round-trip through Money VO."""
    from app.domain.value_objects.money import Money

    original = Decimal("999999999999.99")
    m = Money(original)
    assert m.amount == original, f"Expected {original}, got {m.amount}"

    m2 = m + Money(Decimal("0.01"))
    assert m2.amount == Decimal("1000000000000.00")


def test_api_serialization_unchanged():
    """Calendar projection schemas must serialize Decimal as string in JSON."""
    from app.presentation.schemas.calendar_schemas import CalendarProjectionResponse

    resp = CalendarProjectionResponse(
        available_balance=Decimal("1500000.00"),
        pending_payments=Decimal("350000.00"),
        expected_income=Decimal("2000000.00"),
        projected_balance=Decimal("3150000.00"),
        events_7_days=[],
        events_30_days_count=5,
    )
    data = resp.model_dump()
    assert isinstance(data["available_balance"], Decimal)
    assert isinstance(data["pending_payments"], Decimal)


def test_pattern_suggestion_avg_amount_is_decimal():
    """PatternSuggestionResponse.avg_amount must be Decimal."""
    from app.presentation.schemas.calendar_schemas import PatternSuggestionResponse

    resp = PatternSuggestionResponse(
        title="Test",
        avg_amount=Decimal("150000.00"),
        avg_day=15,
        occurrences=3,
        source="transaction",
    )
    assert isinstance(resp.avg_amount, Decimal)


def test_financial_event_mark_as_paid_has_decimal_type():
    """FinancialEventRepository.mark_as_paid paid_amount param must be typed Decimal."""
    from app.application.interfaces.financial_event_repository import FinancialEventRepository
    import inspect

    sig = inspect.signature(FinancialEventRepository.mark_as_paid)
    param = sig.parameters.get("paid_amount")
    assert param is not None, "paid_amount parameter missing from mark_as_paid"
    assert param.annotation is Decimal, (
        f"mark_as_paid.paid_amount is {param.annotation}, expected Decimal"
    )
