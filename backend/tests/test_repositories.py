import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import date


@pytest.mark.anyio
async def test_repos_return_decimal_amounts(session):
    from app.infrastructure.models.models import (
        DebtPaymentModel,
        BudgetModel,
        RecurringPaymentModel,
        FinancialObligationModel,
        SavingsContributionModel,
    )
    from app.infrastructure.repositories.debt_payment_repository import SQLAlchemyDebtPaymentRepository
    from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
    from app.infrastructure.repositories.recurring_payment_repository import SQLAlchemyRecurringPaymentRepository
    from app.infrastructure.repositories.obligation_repository import SQLAlchemyFinancialObligationRepository
    from app.infrastructure.repositories.savings_contribution_repository import SQLAlchemySavingsContributionRepository

    debt_id = str(uuid4())
    payment = DebtPaymentModel(
        id=str(uuid4()),
        debt_id=debt_id,
        amount=Decimal("100.50"),
        principal=Decimal("80.00"),
        interest=Decimal("20.50"),
        payment_date=date.today(),
        is_reversed=False,
    )
    budget = BudgetModel(
        id=str(uuid4()),
        household_id=str(uuid4()),
        category_id=str(uuid4()),
        amount=Decimal("500000.00"),
        month=1,
        year=2026,
    )
    recurring = RecurringPaymentModel(
        id=str(uuid4()),
        household_id=str(uuid4()),
        account_id=str(uuid4()),
        category_id=str(uuid4()),
        name="Netflix",
        amount=Decimal("45000.00"),
        type="expense",
        frequency="monthly",
        day_of_month=15,
        next_due_date=date(2026, 3, 15),
        is_active=True,
    )
    obligation = FinancialObligationModel(
        id=str(uuid4()),
        household_id=str(uuid4()),
        source="manual",
        name="Arriendo",
        amount=Decimal("1200000.00"),
        currency="COP",
        type="expense",
        frequency="monthly",
        anchor_day=5,
        recommended_offset_days=0,
        cutoff_offset_days=0,
        reminder_days_before=3,
        is_active=True,
    )
    contribution = SavingsContributionModel(
        id=str(uuid4()),
        goal_id=str(uuid4()),
        amount=Decimal("250000.00"),
        contribution_date=date.today(),
    )
    session.add_all([payment, budget, recurring, obligation, contribution])
    await session.flush()

    payment_repo = SQLAlchemyDebtPaymentRepository(session)
    d = await payment_repo.get_by_id(str(payment.id))
    assert isinstance(d["amount"], Decimal)
    assert d["amount"] == Decimal("100.50")
    assert isinstance(d["principal"], Decimal)
    assert d["principal"] == Decimal("80.00")

    budget_repo = SQLAlchemyBudgetRepository(session)
    b = await budget_repo.get_by_id(str(budget.id))
    assert isinstance(b["amount"], Decimal)
    assert b["amount"] == Decimal("500000.00")

    recurring_repo = SQLAlchemyRecurringPaymentRepository(session)
    r = await recurring_repo.get_by_id(str(recurring.id))
    assert isinstance(r["amount"], Decimal)
    assert r["amount"] == Decimal("45000.00")

    obligation_repo = SQLAlchemyFinancialObligationRepository(session)
    o = await obligation_repo.get_by_id(str(obligation.id))
    assert isinstance(o["amount"], Decimal)
    assert o["amount"] == Decimal("1200000.00")

    contribution_repo = SQLAlchemySavingsContributionRepository(session)
    contributions = await contribution_repo.get_by_goal_id(str(contribution.goal_id))
    c = contributions[0]
    assert isinstance(c["amount"], Decimal)
    assert c["amount"] == Decimal("250000.00")
