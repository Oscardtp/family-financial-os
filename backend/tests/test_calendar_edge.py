import pytest
from decimal import Decimal
from datetime import date


class TestCalendarEngine:
    def test_detect_pattern_with_decimal_amounts(self):
        from app.financial_engine.calendar_engine import CalendarEngine
        events = [
            {"title": "Test", "amount": Decimal("100.00"), "due_date": date(2026, 1, 1), "source": "manual", "source_id": "1"},
            {"title": "Test", "amount": Decimal("100.00"), "due_date": date(2026, 2, 1), "source": "manual", "source_id": "1"},
            {"title": "Test", "amount": Decimal("100.00"), "due_date": date(2026, 3, 1), "source": "manual", "source_id": "1"},
        ]
        result = CalendarEngine().detect_pattern(events)
        assert result is not None
        assert result["avg_amount"] == Decimal("100.00")
        assert result["occurrences"] == 3

    def test_detect_pattern_zero_avg_amount(self):
        from app.financial_engine.calendar_engine import CalendarEngine
        events = [
            {"title": "Test", "amount": Decimal("0"), "due_date": date(2026, 1, 1), "source": "manual", "source_id": "1"},
            {"title": "Test", "amount": Decimal("0"), "due_date": date(2026, 2, 1), "source": "manual", "source_id": "1"},
            {"title": "Test", "amount": Decimal("0"), "due_date": date(2026, 3, 1), "source": "manual", "source_id": "1"},
        ]
        result = CalendarEngine().detect_pattern(events)
        assert result is None
