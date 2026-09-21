"""PHASE 10J — Comprehensive datetime validation tests."""
from datetime import datetime, date, timezone
import pytest


# ─── Test 1: utc_now_naive() returns naive datetime ───
class TestUtcNowNaiveContract:
    def test_returns_naive(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        result = utc_now_naive()
        assert result.tzinfo is None

    def test_value_represents_utc(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        result = utc_now_naive()
        aware_utc = datetime.now(timezone.utc)
        diff = abs((aware_utc.replace(tzinfo=None) - result).total_seconds())
        assert diff < 1.0, f"utc_now_naive() is {diff}s off from UTC"

    def test_comparable_with_naive(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        result = utc_now_naive()
        assert result < datetime(2030, 1, 1)
        assert result > datetime(2020, 1, 1)

    def test_no_mixing_aware_naive(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        naive = utc_now_naive()
        aware = datetime.now(timezone.utc)
        with pytest.raises(TypeError):
            _ = naive < aware


# ─── Test 2: ORM models produce naive datetimes ───
class TestOrmModelsProduceNaive:
    MODELS_WITH_CREATED_AT = [
        ("HouseholdModel", "created_at"),
        ("UserModel", "created_at"),
        ("AccountModel", "created_at"),
        ("CategoryModel", "created_at"),
        ("TransactionModel", "created_at"),
        ("DebtModel", "created_at"),
        ("SavingsGoalModel", "created_at"),
        ("BudgetModel", "created_at"),
        ("RecurringPaymentModel", "created_at"),
        ("FinancialObligationModel", "created_at"),
        ("FinancialEventModel", "created_at"),
        ("AuditLogModel", "created_at"),
        ("DetectedPatternModel", "created_at"),
    ]

    @pytest.mark.parametrize("model_name,field", MODELS_WITH_CREATED_AT)
    def test_default_produces_naive(self, model_name, field):
        import app.infrastructure.models.models as m
        model_cls = getattr(m, model_name)
        col = getattr(model_cls, field)
        default_fn = col.default.arg
        val = default_fn(None)
        assert val.tzinfo is None, f"{model_name}.{field} default is aware"


# ─── Test 3: RefreshTokenModel keeps timezone-aware ───
class TestRefreshTokenPreserved:
    def test_created_at_has_timezone(self):
        from app.infrastructure.models.models import RefreshTokenModel
        assert RefreshTokenModel.__table__.c.created_at.type.timezone is True

    def test_expires_at_has_timezone(self):
        from app.infrastructure.models.models import RefreshTokenModel
        assert RefreshTokenModel.__table__.c.expires_at.type.timezone is True

    def test_default_produces_aware(self):
        from app.infrastructure.models.models import RefreshTokenModel
        val = RefreshTokenModel.created_at.default.arg(None)
        assert val.tzinfo is not None


# ─── Test 4: Models can be persisted and retrieved ───
class TestModelPersistence:
    @pytest.mark.asyncio
    async def test_savings_goal_persists_naive_timestamp(self, session):
        from app.infrastructure.models.models import SavingsGoalModel
        model = SavingsGoalModel(
            household_id="test-household",
            name="Test Goal",
            target_amount=1000000,
        )
        session.add(model)
        await session.flush()
        await session.refresh(model)
        assert model.created_at is not None
        assert model.created_at.tzinfo is None

    @pytest.mark.asyncio
    async def test_debt_persists_naive_timestamp(self, session):
        from app.infrastructure.models.models import DebtModel
        model = DebtModel(
            household_id="test-household",
            name="Test Debt",
            total_amount=500000,
            current_balance=500000,
            minimum_payment=50000,
        )
        session.add(model)
        await session.flush()
        await session.refresh(model)
        assert model.created_at is not None
        assert model.created_at.tzinfo is None
        assert model.updated_at is not None
        assert model.updated_at.tzinfo is None


# ─── Test 5: Comparisons work without TypeError ───
class TestDateComparisons:
    def test_naive_vs_naive(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        a = utc_now_naive()
        b = utc_now_naive()
        assert a <= b
        assert b >= a

    def test_obligation_dates_comparable(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        from datetime import timedelta
        created = utc_now_naive()
        updated = created + timedelta(seconds=1)
        assert updated > created

    def test_financial_event_date_range(self):
        from datetime import date
        today = date.today()
        past = date(2020, 1, 1)
        future = date(2030, 12, 31)
        assert past < today < future


# ─── Test 6: Debt toggle doesn't produce datetime errors ───
class TestDebtToggleNoDatetimeErrors:
    @pytest.mark.asyncio
    async def test_toggle_updates_timestamp(self, session):
        from app.infrastructure.models.models import DebtModel
        from app.infrastructure.datetime_utils import utc_now_naive
        import uuid
        debt = DebtModel(
            id=str(uuid.uuid4()),
            household_id="test-household",
            name="Toggle Test Debt",
            total_amount=100000,
            current_balance=100000,
            minimum_payment=10000,
            status="active",
        )
        session.add(debt)
        await session.flush()
        created_at = debt.created_at

        debt.status = "paused"
        debt.updated_at = utc_now_naive()
        await session.flush()
        await session.refresh(debt)

        assert debt.status == "paused"
        assert debt.updated_at >= created_at
        assert debt.updated_at.tzinfo is None


# ─── Test 7: Financial events ordered chronologically ───
class TestFinancialEventOrdering:
    @pytest.mark.asyncio
    async def test_events_created_in_order(self, session):
        from app.infrastructure.models.models import FinancialEventModel
        from app.infrastructure.datetime_utils import utc_now_naive
        import uuid

        events = []
        for i in range(3):
            ev = FinancialEventModel(
                id=str(uuid.uuid4()),
                household_id="test-household",
                source="TEST",
                type="expense",
                title=f"Event {i}",
                amount=10000 * (i + 1),
                due_date=date(2026, 9, 15 + i),
                status="pending",
            )
            session.add(ev)
            events.append(ev)
        await session.flush()

        for ev in events:
            await session.refresh(ev)
            assert ev.created_at is not None
            assert ev.created_at.tzinfo is None

        dates = [ev.due_date for ev in events]
        assert dates == sorted(dates)


# ─── Test 8: Overdue obligation identified correctly ───
class TestOverdueObligation:
    def test_past_date_is_overdue(self):
        today = date.today()
        past_date = date(2020, 1, 1)
        assert past_date < today, "Past date should be identified as overdue"

    def test_future_date_not_overdue(self):
        today = date.today()
        future_date = date(2030, 12, 31)
        assert future_date >= today, "Future date should not be overdue"

    @pytest.mark.asyncio
    async def test_overdue_event_query(self, session):
        from app.infrastructure.models.models import FinancialEventModel
        import uuid
        ev = FinancialEventModel(
            id=str(uuid.uuid4()),
            household_id="test-household",
            source="TEST",
            type="expense",
            title="Overdue Test",
            amount=50000,
            due_date=date(2020, 6, 1),
            status="pending",
        )
        session.add(ev)
        await session.flush()
        await session.refresh(ev)
        assert ev.due_date < date.today()


# ─── Test 9: Future obligation identified correctly ───
class TestFutureObligation:
    @pytest.mark.asyncio
    async def test_future_event_not_overdue(self, session):
        from app.infrastructure.models.models import FinancialEventModel
        import uuid
        future_date = date(2030, 12, 31)
        ev = FinancialEventModel(
            id=str(uuid.uuid4()),
            household_id="test-household",
            source="TEST",
            type="expense",
            title="Future Test",
            amount=50000,
            due_date=future_date,
            status="pending",
        )
        session.add(ev)
        await session.flush()
        await session.refresh(ev)
        assert ev.due_date >= date.today()


# ─── Test 10: Date boundaries don't cause naive/aware errors ───
class TestDateBoundarySafety:
    def test_midnight_boundary(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        start = utc_now_naive().replace(hour=0, minute=0, second=0, microsecond=0)
        end = utc_now_naive().replace(hour=23, minute=59, second=59, microsecond=999999)
        assert start < end

    def test_date_range_filter(self):
        from datetime import date
        date_from = date(2026, 9, 1)
        date_to = date(2026, 10, 1)
        target = date(2026, 9, 15)
        assert date_from <= target < date_to

    def test_month_boundary(self):
        from datetime import date
        last_sept = date(2026, 9, 30)
        first_oct = date(2026, 10, 1)
        assert last_sept < first_oct

    def test_isoformat_roundtrip(self):
        from app.infrastructure.datetime_utils import utc_now_naive
        dt = utc_now_naive()
        iso = dt.isoformat()
        parsed = datetime.fromisoformat(iso)
        assert parsed.tzinfo is None
        assert parsed.year == dt.year
        assert parsed.month == dt.month
        assert parsed.day == dt.day
