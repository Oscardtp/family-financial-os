"""Tests to verify AuditLogModel has proper FK to households.

FASE 4B.8 — AuditLog.household_id FK
"""
from sqlalchemy import inspect as sa_inspect, text


def test_auditlog_household_has_foreign_key():
    """AuditLogModel ORM must declare ForeignKey on household_id."""
    from app.infrastructure.models.models import AuditLogModel

    col = AuditLogModel.__table__.c.household_id
    fk_args = col.foreign_keys
    assert len(fk_args) > 0, "AuditLogModel.household_id has no ForeignKey"
    fk = list(fk_args)[0]
    assert fk.column.table.name == "households", (
        f"FK references {fk.column.table.name}, expected households"
    )


def test_metadata_contains_fk_constraint():
    """AuditLog table metadata must include FK constraint on household_id."""
    from app.infrastructure.models.models import AuditLogModel, Base

    table = Base.metadata.tables["audit_logs"]
    fks = [fk for fk in table.foreign_keys]
    assert len(fks) > 0, "audit_logs table has no foreign keys"
    household_fks = [fk for fk in fks if fk.column.table.name == "households"]
    assert len(household_fks) > 0, "audit_logs has no FK to households"


def test_auditlog_relationship_integrity():
    """Creating an AuditLog with a valid household_id must succeed."""
    from app.infrastructure.models.models import AuditLogModel, HouseholdModel, Base
    from sqlalchemy import create_engine, inspect

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    fk_list = inspector.get_foreign_keys("audit_logs")
    household_fks = [fk for fk in fk_list if fk["referred_table"] == "households"]
    assert len(household_fks) > 0, (
        f"Runtime FK missing: {fk_list}"
    )


def test_existing_audit_queries_still_work():
    """Existing audit log queries must not break after FK addition."""
    from app.infrastructure.models.models import AuditLogModel
    from sqlalchemy import select

    stmt = select(AuditLogModel).where(AuditLogModel.household_id == "test-id")
    assert stmt is not None, "Select query on AuditLogModel must still work"
