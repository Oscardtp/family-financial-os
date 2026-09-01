"""Initialize database with Alembic migrations.

Usage:
    python init_db.py          # Apply all pending migrations
    python init_db.py reset    # Delete DB and recreate (DEV ONLY)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from alembic.config import Config
from alembic import command
from app.config import DB_FILE


def _get_alembic_cfg():
    cfg = Config(str(Path(__file__).resolve().parent / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{DB_FILE}")
    return cfg


def init_db():
    print(f"Database: {DB_FILE}")
    command.upgrade(_get_alembic_cfg(), "head")
    print("Migrations applied successfully")


def reset_db():
    if DB_FILE.exists():
        DB_FILE.unlink()
        print(f"Deleted: {DB_FILE}")
    init_db()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_db()
    else:
        init_db()
