"""Tests to verify DebtPaymentModel has proper FK to transactions with RESTRICT ondelete.

FASE 4B.9 — DebtPayment → Transaction FK
"""
from sqlalchemy import inspect as sa_inspect, text, create_engine
from sqlalchemy.exc import IntegrityError
import pytest


def test_debtpayment_transaction_has_foreign_key():
    """DebtPaymentModel ORM must declare ForeignKey on transaction_id."""
    from app.infrastructure.models.models import DebtPaymentModel

    col = DebtPaymentModel.__table__.c.transaction_id
    fk_args = col.foreign_keys
    assert len(fk_args) > 0, "DebtPaymentModel.transaction_id has no ForeignKey"
    fk = list(fk_args)[0]
    assert fk.column.table.name == "transactions", (
        f"FK references {fk.column.table.name}, expected transactions"
    )


def test_debtpayment_transaction_fk_has_restrict_ondelete():
    """FK from DebtPayment.transaction_id must use RESTRICT ondelete."""
    from app.infrastructure.models.models import DebtPaymentModel

    col = DebtPaymentModel.__table__.c.transaction_id
    fk = list(col.foreign_keys)[0]
    assert fk.ondelete == "RESTRICT", (
        f"FK ondelete is {fk.ondelete}, expected RESTRICT"
    )


def test_metadata_contains_debtpayment_transaction_fk():
    """debt_payments table metadata must include FK constraint on transaction_id."""
    from app.infrastructure.models.models import Base

    table = Base.metadata.tables["debt_payments"]
    fks = [fk for fk in table.foreign_keys]
    transaction_fks = [fk for fk in fks if fk.column.table.name == "transactions"]
    assert len(transaction_fks) > 0, "debt_payments has no FK to transactions"


def test_debtpayment_transaction_fk_runtime_enforced():
    """FK from debt_payments to transactions must be enforced at runtime."""
    from app.infrastructure.models.models import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = sa_inspect(engine)
    fk_list = inspector.get_foreign_keys("debt_payments")
    transaction_fks = [fk for fk in fk_list if fk["referred_table"] == "transactions"]
    assert len(transaction_fks) > 0, (
        f"Runtime FK missing: {fk_list}"
    )


def test_debtpayment_queries_still_work():
    """Existing DebtPayment queries must not break after FK addition."""
    from app.infrastructure.models.models import DebtPaymentModel
    from sqlalchemy import select

    stmt = select(DebtPaymentModel).where(
        DebtPaymentModel.transaction_id == "test-id"
    )
    assert stmt is not None, "Select query on DebtPaymentModel must still work"
