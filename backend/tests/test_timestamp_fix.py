"""Tests for the UTC-naive timestamp fix (PHASE 10I)."""
from datetime import datetime, timezone
import pytest


class TestUtcNowNaive:
    """Test F — utc_now_naive() helper."""

    def test_returns_naive_datetime(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        result = utc_now_naive()
        assert result.tzinfo is None

    def test_returns_utc_equivalent(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        result = utc_now_naive()
        aware = datetime.now(timezone.utc)
        diff = abs((aware.replace(tzinfo=None) - result).total_seconds())
        assert diff < 1.0

    def test_comparable_with_naive(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        result = utc_now_naive()
        assert result < datetime(2030, 1, 1)
        assert result > datetime(2020, 1, 1)


class TestRefreshTokenTimezone:
    """Test E — RefreshTokenModel must keep DateTime(timezone=True)."""

    def test_refresh_token_created_at_has_timezone(self):
        from app.infrastructure.models.models import RefreshTokenModel
        col = RefreshTokenModel.__table__.c.created_at
        assert col.type.timezone is True

    def test_refresh_token_expires_at_has_timezone(self):
        from app.infrastructure.models.models import RefreshTokenModel
        col = RefreshTokenModel.__table__.c.expires_at
        assert col.type.timezone is True

    def test_refresh_token_default_produces_aware(self):
        """RefreshTokenModel still uses datetime.now(timezone.utc) directly."""
        from app.infrastructure.models.models import RefreshTokenModel
        val = RefreshTokenModel.created_at.default.arg(None)
        assert val.tzinfo is not None


class TestOrmModelsNaive:
    """Verify ORM models produce naive datetimes via utc_now_naive()."""

    def test_household_created_at_naive(self):
        from app.infrastructure.models.models import HouseholdModel
        val = HouseholdModel.created_at.default.arg(None)
        assert val.tzinfo is None

    def test_savings_goal_created_at_naive(self):
        from app.infrastructure.models.models import SavingsGoalModel
        val = SavingsGoalModel.created_at.default.arg(None)
        assert val.tzinfo is None

    def test_debt_created_at_naive(self):
        from app.infrastructure.models.models import DebtModel
        val = DebtModel.created_at.default.arg(None)
        assert val.tzinfo is None

    def test_financial_event_created_at_naive(self):
        from app.infrastructure.models.models import FinancialEventModel
        val = FinancialEventModel.created_at.default.arg(None)
        assert val.tzinfo is None

    def test_refresh_token_still_aware(self):
        from app.infrastructure.models.models import RefreshTokenModel
        val = RefreshTokenModel.created_at.default.arg(None)
        assert val.tzinfo is not None
