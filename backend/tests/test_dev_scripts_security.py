"""Tests to ensure dev scripts contain no hardcoded credentials.

FASE 4B.6 — Dev Scripts Security
"""
import re
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
BACKEND_DIR = Path(__file__).resolve().parent.parent

DANGEROUS_PATTERNS = [
    r"['\"]admin123['\"]",
    r"['\"]familia123['\"]",
    r"['\"]password123['\"]",
    r"\$2b\$\d+\$",
    r"hash_password\(['\"][^'\"]+['\"]\)",
]

DEV_SCRIPTS = [
    BACKEND_DIR / "verify_sync.py",
    BACKEND_DIR / "seed_deudas.py",
    BACKEND_DIR / "check_pwd.py",
    SCRIPTS_DIR / "backup_db.py",
    SCRIPTS_DIR / "run_backup.ps1",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def test_scripts_do_not_contain_default_passwords():
    """None of the dev scripts should contain known default passwords."""
    for script in DEV_SCRIPTS:
        if not script.exists():
            continue
        content = _read(script)
        for pattern in DANGEROUS_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert not matches, (
                f"{script.name} contains dangerous pattern '{pattern}': {matches}"
            )


def test_scripts_require_env_or_prompt():
    """verify_sync.py and seed_deudas.py must read credentials from env, not hardcode."""
    for name in ("verify_sync.py", "seed_deudas.py"):
        path = BACKEND_DIR / name
        if not path.exists():
            continue
        content = _read(path)
        assert "os.environ" in content or "getpass" in content or "os.getenv" in content, (
            f"{name} must read credentials from environment variables or prompt"
        )


def test_example_credentials_are_not_used():
    """No script should contain the bcrypt hash or password list from check_pwd.py."""
    check_pwd = BACKEND_DIR / "check_pwd.py"
    if not check_pwd.exists():
        return
    content = _read(check_pwd)
    assert "admin123" not in content, "check_pwd.py still contains 'admin123'"
    assert "familia123" not in content, "check_pwd.py still contains 'familia123'"
    assert "$2b$12$" not in content, "check_pwd.py still contains a hardcoded bcrypt hash"
