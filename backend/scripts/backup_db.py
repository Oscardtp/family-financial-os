import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_ROOT / "family_financial.db"
BACKUP_DIR = PROJECT_ROOT / "backups"
MAX_BACKUPS = 15


def create_backup():
    if not DB_FILE.exists():
        print(f"DB not found: {DB_FILE}")
        return False

    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"family_financial_{timestamp}.zip"
    backup_path = BACKUP_DIR / backup_name

    try:
        with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(DB_FILE, DB_FILE.name)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

    backups = sorted(BACKUP_DIR.glob("family_financial_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in backups[MAX_BACKUPS:]:
        try:
            old.unlink()
            print(f"Removed old backup: {old.name}")
        except Exception as e:
            print(f"Could not remove {old.name}: {e}")

    return True


if __name__ == "__main__":
    ok = create_backup()
    if not ok:
        raise SystemExit(1)
