"""HF4 - Integridad de la cadena Alembic (regresiones de esquema).

Dos invariantes que una instalación limpia necesita para funcionar:

1. Ninguna columna puede ser añadida por dos migraciones distintas
   (el bug de HF4: debt_payments.is_reversed duplicada rompía
   `alembic upgrade head` con DuplicateColumn).
2. Toda tabla definida en los modelos SQLAlchemy debe ser creada por
   alguna migración (si no, la DB limpia queda incompleta aunque
   `upgrade head` termine sin error).
"""

import re
from pathlib import Path

from app.database import Base
import app.infrastructure.models.models  # noqa: F401  (registra los modelos en Base.metadata)

VERSIONS_DIR = Path(__file__).resolve().parents[1] / "alembic" / "versions"


def _migration_sources() -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(VERSIONS_DIR.glob("*.py"))
        if not path.name.startswith("__")
    }


def _revision_of(source: str, fallback: str) -> str:
    match = re.search(r"revision\s*[:=]\s*['\"]([^'\"]+)['\"]", source)
    return match.group(1) if match else fallback


def _created_tables() -> set[str]:
    created: set[str] = set()
    for source in _migration_sources().values():
        created |= set(re.findall(r"op\.create_table\(\s*['\"]([^'\"]+)['\"]", source))
    return created


def test_no_column_is_added_by_two_migrations():
    owners: dict[str, list[str]] = {}
    for filename, source in _migration_sources().items():
        revision = _revision_of(source, filename)
        for table, column in re.findall(
            r"op\.add_column\(\s*['\"]([^'\"]+)['\"]\s*,\s*sa\.Column\(\s*['\"]([^'\"]+)['\"]",
            source,
        ):
            owners.setdefault(f"{table}.{column}", []).append(revision)

    duplicated = {key: revs for key, revs in owners.items() if len(revs) > 1}
    assert not duplicated, f"Columnas añadidas por más de una migración: {duplicated}"


def test_every_model_table_is_created_by_a_migration():
    missing = sorted(set(Base.metadata.tables) - _created_tables())
    assert not missing, f"Tablas del modelo sin migración que las cree: {missing}"
