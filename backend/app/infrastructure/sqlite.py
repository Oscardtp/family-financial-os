"""Infrastructure layer: SQLite repository for Family Financial OS.

Este módulo define la capa de persistencia. La lógica financiera
no toca al repositorio: el dominio se comunica a través de interfaces
(protocolos en Python) definidas en la aplicación.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
import sqlite3
import os

from app.domain.domain import (
    Money, Timestamp, Account, AccountType, Transaction,
    TransactionType, TransactionStatus, Budget, Debt, Goal,
    Asset, Liability, Member, Household, User, Session,
    Transfer, LedgerEntry, RecurringPayment, DebtPayment, GoalContribution,
    Category, Notification
)


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "finance.db")


def get_db_path():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return DB_PATH


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas si no existen."""
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS households (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        country TEXT DEFAULT 'CO',
        currency TEXT DEFAULT 'COP',
        timezone TEXT DEFAULT 'America/Bogota',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        household_id TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        household_id TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS members (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        household_id TEXT NOT NULL,
        role TEXT DEFAULT 'adult',
        status TEXT DEFAULT 'active',
        email TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        currency TEXT NOT NULL,
        balance INTEGER NOT NULL,
        account_number TEXT,
        household_id TEXT NOT NULL,
        member_id TEXT,
        status TEXT DEFAULT 'active',
        initial_balance INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        household_id TEXT NOT NULL,
        parent_id TEXT,
        color TEXT,
        icon TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE,
        FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        account_id TEXT NOT NULL,
        category_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount INTEGER NOT NULL,
        currency TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        household_id TEXT NOT NULL,
        member_id TEXT,
        status TEXT DEFAULT 'processed',
        reference TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS transfers (
        id TEXT PRIMARY KEY,
        from_account_id TEXT NOT NULL,
        to_account_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        currency TEXT NOT NULL,
        date TEXT NOT NULL,
        household_id TEXT NOT NULL,
        description TEXT,
        reference TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (from_account_id) REFERENCES accounts(id) ON DELETE CASCADE,
        FOREIGN KEY (to_account_id) REFERENCES accounts(id) ON DELETE CASCADE,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ledger_entries (
        id TEXT PRIMARY KEY,
        transaction_id TEXT NOT NULL,
        account_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount INTEGER NOT NULL,
        balance_before INTEGER NOT NULL,
        balance_after INTEGER NOT NULL,
        household_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS budgets (
        id TEXT PRIMARY KEY,
        household_id TEXT NOT NULL,
        category_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        period TEXT NOT NULL DEFAULT 'monthly',
        year INTEGER NOT NULL,
        month INTEGER,
        spent INTEGER NOT NULL DEFAULT 0,
        currency TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS recurring_payments (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        amount INTEGER NOT NULL,
        frequency TEXT NOT NULL,
        category_id TEXT NOT NULL,
        account_id TEXT NOT NULL,
        household_id TEXT NOT NULL,
        day_of_month INTEGER,
        next_due_date TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS debts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        principal INTEGER NOT NULL,
        interest_rate REAL NOT NULL,
        monthly_payment INTEGER NOT NULL,
        currency TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL,
        household_id TEXT NOT NULL,
        creditor TEXT,
        installments INTEGER,
        start_date TEXT,
        balance INTEGER NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS debt_payments (
        id TEXT PRIMARY KEY,
        debt_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        date TEXT NOT NULL,
        household_id TEXT NOT NULL,
        account_id TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE CASCADE,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        target_amount INTEGER NOT NULL,
        currency TEXT NOT NULL,
        household_id TEXT NOT NULL,
        target_date TEXT,
        current_amount INTEGER NOT NULL DEFAULT 0,
        is_completed INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS goal_contributions (
        id TEXT PRIMARY KEY,
        goal_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        date TEXT NOT NULL,
        household_id TEXT NOT NULL,
        account_id TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        value INTEGER NOT NULL,
        currency TEXT NOT NULL,
        household_id TEXT NOT NULL,
        acquired_date TEXT NOT NULL,
        description TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS liabilities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        amount INTEGER NOT NULL,
        currency TEXT NOT NULL,
        household_id TEXT NOT NULL,
        due_date TEXT NOT NULL,
        creditor TEXT,
        interest_rate REAL,
        description TEXT,
        is_debt INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()


class SQLiteRepository:
    """Repositorio SQLite genérico para el dominio."""

    def __init__(self):
        self._db_path = get_db_path()

    def _connect(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _commit(self):
        conn = self._connect()
        conn.commit()
        return conn

    def _close(self, conn):
        conn.close()

    # ── Household ──────────────────────────

    def create_household(self, household: Household) -> Household:
        conn = self._connect()
        conn.execute(
            "INSERT INTO households (id, name, country, currency, timezone, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                household.id, household.name,
                household.country, household.currency, household.timezone,
                household.created_at.to_iso(), household.updated_at.to_iso(),
            ),
        )
        conn.commit()
        conn.close()
        return household

    def get_household(self, household_id: str) -> Optional[Household]:
        conn = self._connect()
        row = conn.execute(
            "SELECT * FROM households WHERE id = ?",
            (household_id,),
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return Household(
            id=row["id"], name=row["name"],
            country=row["country"], currency=row["currency"], timezone=row["timezone"],
            created_at=Timestamp(row["created_at"]),
            updated_at=Timestamp(row["updated_at"]),
        )

    def get_households(self) -> List[Household]:
        conn = self._connect()
        rows = conn.execute("SELECT * FROM households").fetchall()
        conn.close()
        return [
            Household(
                id=r["id"], name=r["name"],
                country=r["country"], currency=r["currency"], timezone=r["timezone"],
                created_at=Timestamp(r["created_at"]),
                updated_at=Timestamp(r["updated_at"]),
            )
            for r in rows
        ]

    def update_household(self, household: Household) -> Household:
        conn = self._connect()
        conn.execute(
            "UPDATE households SET name = ?, country = ?, currency = ?, timezone = ?, updated_at = ? WHERE id = ?",
            (household.name, household.country, household.currency, household.timezone,
             household.updated_at.to_iso(), household.id),
        )
        conn.commit()
        conn.close()
        return household

    def delete_household(self, household_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM households WHERE id = ?", (household_id,))
        conn.commit()
        conn.close()

    # ── Users ──────────────────────────────

    def create_user(self, user: User) -> User:
        conn = self._connect()
        conn.execute(
            "INSERT INTO users (id, name, email, password_hash, household_id, is_active, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user.id, user.name, user.email, user.password_hash, user.household_id,
             1 if user.is_active else 0, user.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if row is None:
            return None
        return User(
            id=row["id"], name=row["name"], email=row["email"],
            password_hash=row["password_hash"], household_id=row["household_id"],
            is_active=bool(row["is_active"]), created_at=Timestamp(row["created_at"]),
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return self.get_user_by_email(email)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return User(
            id=row["id"], name=row["name"], email=row["email"],
            password_hash=row["password_hash"], household_id=row["household_id"],
            is_active=bool(row["is_active"]), created_at=Timestamp(row["created_at"]),
        )

    # ── Sessions ───────────────────────────

    def create_session(self, session: Session) -> Session:
        conn = self._connect()
        conn.execute(
            "INSERT INTO sessions (id, user_id, household_id, expires_at, is_active, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (session.id, session.user_id, session.household_id, session.expires_at.to_iso(),
             1 if session.is_active else 0, session.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Session(
            id=row["id"], user_id=row["user_id"], household_id=row["household_id"],
            expires_at=Timestamp(row["expires_at"]), is_active=bool(row["is_active"]),
            created_at=Timestamp(row["created_at"]),
        )

    def delete_session(self, session_id: str) -> None:
        conn = self._connect()
        conn.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

    # ── Members ───────────────────────────

    def create_member(self, member: Member) -> Member:
        conn = self._connect()
        conn.execute(
            "INSERT INTO members (id, name, household_id, role, status, email, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (member.id, member.name, member.household_id, member.role, member.status,
             member.email, member.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return member

    def get_members(self, household_id: str) -> List[Member]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM members WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Member(id=r["id"], name=r["name"], household_id=r["household_id"],
                   role=r["role"], status=r["status"], email=r["email"],
                   created_at=Timestamp(r["created_at"]))
            for r in rows
        ]

    def get_member(self, member_id: str) -> Optional[Member]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Member(id=row["id"], name=row["name"], household_id=row["household_id"],
                      role=row["role"], status=row["status"], email=row["email"],
                      created_at=Timestamp(row["created_at"]))

    # ── Accounts ───────────────────────────

    def create_account(self, account: Account) -> Account:
        conn = self._connect()
        conn.execute(
            "INSERT INTO accounts (id, name, type, currency, balance, account_number, household_id, member_id, status, initial_balance, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (account.id, account.name, account.account_type, account.currency,
             account.balance.value, account.account_number, account.household_id,
             account.member_id, account.status, account.initial_balance.value,
             account.created_at.to_iso(), account.updated_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        conn = self._connect()
        row = conn.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return Account(
            id=row["id"], name=row["name"], account_type=AccountType(row["type"]),
            currency=row["currency"], balance=Money(row["balance"], row["currency"], 2),
            household_id=row["household_id"], member_id=row["member_id"],
            account_number=row["account_number"], status=row["status"],
            initial_balance=Money(row["initial_balance"], row["currency"], 2),
            created_at=Timestamp(row["created_at"]),
            updated_at=Timestamp(row["updated_at"]),
        )

    def get_accounts_by_household(self, household_id: str) -> List[Account]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM accounts WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Account(
                id=r["id"], name=r["name"], account_type=AccountType(r["type"]),
                currency=r["currency"], balance=Money(r["balance"], r["currency"], 2),
                household_id=r["household_id"], member_id=r["member_id"],
                account_number=r["account_number"], status=r["status"],
                initial_balance=Money(r["initial_balance"], r["currency"], 2),
                created_at=Timestamp(r["created_at"]),
                updated_at=Timestamp(r["updated_at"]),
            )
            for r in rows
        ]

    def get_account_balance(self, account_id: str) -> Optional[Money]:
        conn = self._connect()
        row = conn.execute(
            "SELECT balance, currency FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return Money(row["balance"], row["currency"], 2)

    def update_account_balance(self, account_id: str, new_balance: Money) -> None:
        conn = self._connect()
        conn.execute("UPDATE accounts SET balance = ?, updated_at = ? WHERE id = ?",
                     (new_balance.value, datetime.now().isoformat(), account_id))
        conn.commit()
        conn.close()

    def delete_account(self, account_id: str, household_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM accounts WHERE id = ? AND household_id = ?",
                     (account_id, household_id))
        conn.commit()
        conn.close()

    # ── Categories ──────────────────────────

    def create_category(self, category: Category) -> Category:
        conn = self._connect()
        conn.execute(
            "INSERT INTO categories (id, name, type, household_id, parent_id, color, icon, is_active, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (category.id, category.name, category.type, category.household_id,
             category.parent_id, category.color, category.icon, int(category.is_active),
             category.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return category

    def get_categories(self, household_id: str) -> List[Category]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM categories WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Category(id=r["id"], name=r["name"], type=r["type"],
                     household_id=r["household_id"], parent_id=r["parent_id"],
                     color=r["color"], icon=r["icon"], is_active=bool(r["is_active"]),
                     created_at=Timestamp(r["created_at"]))
            for r in rows
        ]

    def get_category(self, category_id: str) -> Optional[Category]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Category(id=row["id"], name=row["name"], type=row["type"],
                        household_id=row["household_id"], parent_id=row["parent_id"],
                        color=row["color"], icon=row["icon"], is_active=bool(row["is_active"]),
                        created_at=Timestamp(row["created_at"]))

    # ── Transactions ───────────────────────

    def create_transaction(self, transaction: Transaction) -> Transaction:
        conn = self._connect()
        conn.execute(
            "INSERT INTO transactions (id, account_id, category_id, type, amount, currency, description, date, household_id, member_id, status, reference, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (transaction.id, transaction.account_id, transaction.category_id, transaction.type,
             transaction.amount.value, transaction.amount.currency, transaction.description,
             transaction.date.to_iso(), transaction.household_id, transaction.member_id,
             transaction.status, transaction.reference, transaction.notes,
             transaction.created_at.to_iso(), transaction.updated_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return transaction

    def get_transactions(self, household_id: str) -> List[Transaction]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM transactions WHERE household_id = ? AND status != 'cancelled' ORDER BY date DESC",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Transaction(
                id=r["id"], account_id=r["account_id"], category_id=r["category_id"],
                type=r["type"], amount=Money(r["amount"], r["currency"], 2),
                description=r["description"], date=Timestamp(r["date"]),
                household_id=r["household_id"], member_id=r["member_id"],
                status=r["status"], reference=r["reference"], notes=r["notes"],
                created_at=Timestamp(r["created_at"]),
                updated_at=Timestamp(r["updated_at"]),
            )
            for r in rows
        ]

    def get_transactions_by_account(self, account_id: str) -> List[Transaction]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM transactions WHERE account_id = ? AND status != 'cancelled' ORDER BY date DESC",
            (account_id,),
        ).fetchall()
        conn.close()
        return [
            Transaction(
                id=r["id"], account_id=r["account_id"], category_id=r["category_id"],
                type=r["type"], amount=Money(r["amount"], r["currency"], 2),
                description=r["description"], date=Timestamp(r["date"]),
                household_id=r["household_id"], member_id=r["member_id"],
                status=r["status"], reference=r["reference"], notes=r["notes"],
                created_at=Timestamp(r["created_at"]),
                updated_at=Timestamp(r["updated_at"]),
            )
            for r in rows
        ]

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Transaction(
            id=row["id"], account_id=row["account_id"], category_id=row["category_id"],
            type=row["type"], amount=Money(row["amount"], row["currency"], 2),
            description=row["description"], date=Timestamp(row["date"]),
            household_id=row["household_id"], member_id=row["member_id"],
            status=row["status"], reference=row["reference"], notes=row["notes"],
            created_at=Timestamp(row["created_at"]),
            updated_at=Timestamp(row["updated_at"]),
        )

    def get_transaction_count(self, household_id: str) -> int:
        conn = self._connect()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM transactions WHERE household_id = ? AND status != 'cancelled'",
            (household_id,),
        ).fetchone()
        conn.close()
        return row["cnt"]

    def get_transactions_by_date_range(self, household_id: str, start: str, end: str) -> List[Transaction]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM transactions WHERE household_id = ? AND status != 'cancelled' AND date BETWEEN ? AND ? ORDER BY date DESC",
            (household_id, start, end),
        ).fetchall()
        conn.close()
        return [
            Transaction(
                id=r["id"], account_id=r["account_id"], category_id=r["category_id"],
                type=r["type"], amount=Money(r["amount"], r["currency"], 2),
                description=r["description"], date=Timestamp(r["date"]),
                household_id=r["household_id"], member_id=r["member_id"],
                status=r["status"], reference=r["reference"], notes=r["notes"],
                created_at=Timestamp(r["created_at"]),
                updated_at=Timestamp(r["updated_at"]),
            )
            for r in rows
        ]

    def update_transaction(self, transaction: Transaction) -> Transaction:
        conn = self._connect()
        conn.execute(
            "UPDATE transactions SET account_id = ?, category_id = ?, type = ?, amount = ?, "
            "description = ?, date = ?, member_id = ?, status = ?, reference = ?, notes = ?, updated_at = ? "
            "WHERE id = ?",
            (
                transaction.account_id, transaction.category_id, transaction.type,
                transaction.amount.value, transaction.description, transaction.date.to_iso(),
                transaction.member_id, transaction.status, transaction.reference,
                transaction.notes, transaction.updated_at.to_iso(),
                transaction.id,
            ),
        )
        conn.commit()
        conn.close()
        return transaction

    def delete_transaction(self, transaction_id: str, household_id: str) -> None:
        conn = self._connect()
        conn.execute("UPDATE transactions SET status = 'cancelled' WHERE id = ? AND household_id = ?",
                     (transaction_id, household_id))
        conn.commit()
        conn.close()

    # ── Budgets ────────────────────────────

    def create_budget(self, budget: Budget) -> Budget:
        conn = self._connect()
        conn.execute(
            "INSERT INTO budgets (id, household_id, category_id, amount, period, year, month, spent, currency, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (budget.id, budget.household_id, budget.category_id, budget.amount.value,
             budget.period, budget.year, budget.month, budget.spent.value, budget.amount.currency,
             budget.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return budget

    def get_budgets(self, household_id: str) -> List[Budget]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM budgets WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Budget(
                id=r["id"], household_id=r["household_id"], category_id=r["category_id"],
                amount=Money(r["amount"], r["currency"], 2), period=r["period"],
                year=r["year"], month=r["month"], spent=Money(r["spent"], r["currency"], 2),
                created_at=Timestamp(r["created_at"]),
            )
            for r in rows
        ]

    def get_budget(self, budget_id: str) -> Optional[Budget]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM budgets WHERE id = ?", (budget_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Budget(
            id=row["id"], household_id=row["household_id"], category_id=row["category_id"],
            amount=Money(row["amount"], row["currency"], 2), period=row["period"],
            year=row["year"], month=row["month"], spent=Money(row["spent"], row["currency"], 2),
            created_at=Timestamp(row["created_at"]),
        )

    def update_budget(self, budget_id: str, updates: dict) -> Budget:
        conn = self._connect()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [budget_id]
        conn.execute(f"UPDATE budgets SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return self.get_budget(budget_id)

    def delete_budget(self, budget_id: str, household_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM budgets WHERE id = ? AND household_id = ?",
                     (budget_id, household_id))
        conn.commit()
        conn.close()

    # ── Debts ──────────────────────────────

    def create_debt(self, debt: Debt) -> Debt:
        conn = self._connect()
        conn.execute(
            "INSERT INTO debts (id, name, principal, interest_rate, monthly_payment, currency, due_date, status, created_at, household_id, creditor, installments, start_date, balance) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (debt.id, debt.name, debt.principal.value, float(debt.interest_rate),
             debt.monthly_payment.value, debt.currency, debt.due_date.to_iso(),
             debt.status, debt.created_at.to_iso(), debt.household_id,
             debt.creditor, debt.installments,
             debt.start_date.to_iso() if debt.start_date else None, debt.balance.value),
        )
        conn.commit()
        conn.close()
        return debt

    def get_debts(self, household_id: str) -> List[Debt]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM debts WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Debt(
                id=r["id"], name=r["name"], principal=Money(r["principal"], r["currency"], 2),
                interest_rate=Decimal(str(r["interest_rate"])), monthly_payment=Money(r["monthly_payment"], r["currency"], 2),
                currency=r["currency"], due_date=Timestamp(r["due_date"]),
                status=r["status"], created_at=Timestamp(r["created_at"]),
                household_id=r["household_id"], creditor=r["creditor"],
                installments=r["installments"],
                start_date=Timestamp(r["start_date"]) if r["start_date"] else None,
                balance=Money(r["balance"], r["currency"], 2),
            )
            for r in rows
        ]

    def get_debt(self, debt_id: str) -> Optional[Debt]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM debts WHERE id = ?", (debt_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Debt(
            id=row["id"], name=row["name"], principal=Money(row["principal"], row["currency"], 2),
            interest_rate=Decimal(str(row["interest_rate"])), monthly_payment=Money(row["monthly_payment"], row["currency"], 2),
            currency=row["currency"], due_date=Timestamp(row["due_date"]),
            status=row["status"], created_at=Timestamp(row["created_at"]),
            household_id=row["household_id"], creditor=row["creditor"],
            installments=row["installments"],
            start_date=Timestamp(row["start_date"]) if row["start_date"] else None,
            balance=Money(row["balance"], row["currency"], 2),
        )

    def update_debt(self, debt: Debt) -> Debt:
        conn = self._connect()
        conn.execute(
            "UPDATE debts SET name = ?, principal = ?, interest_rate = ?, monthly_payment = ?, "
            "currency = ?, due_date = ?, status = ?, created_at = ?, creditor = ?, installments = ?, start_date = ?, balance = ? WHERE id = ?",
            (debt.name, debt.principal.value, float(debt.interest_rate), debt.monthly_payment.value,
             debt.currency, debt.due_date.to_iso(), debt.status, debt.created_at.to_iso(),
             debt.creditor, debt.installments,
             debt.start_date.to_iso() if debt.start_date else None, debt.balance.value,
             debt.id),
        )
        conn.commit()
        conn.close()
        return debt

    def delete_debt(self, debt_id: str, household_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM debts WHERE id = ? AND household_id = ?",
                     (debt_id, household_id))
        conn.commit()
        conn.close()

    # ── Goals ──────────────────────────────

    def create_goal(self, goal: Goal) -> Goal:
        conn = self._connect()
        conn.execute(
            "INSERT INTO goals (id, name, target_amount, currency, household_id, target_date, current_amount, is_completed, is_active, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (goal.id, goal.name, goal.target_amount.value, goal.currency, goal.household_id,
             goal.target_date.to_iso() if goal.target_date else None,
             goal.current_amount.value, int(goal.is_completed), int(goal.is_active),
             goal.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return goal

    def get_goals(self, household_id: str) -> List[Goal]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM goals WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Goal(
                id=r["id"], name=r["name"], target_amount=Money(r["target_amount"], r["currency"], 2),
                currency=r["currency"], household_id=r["household_id"],
                target_date=Timestamp(r["target_date"]) if r["target_date"] else None,
                current_amount=Money(r["current_amount"], r["currency"], 2),
                is_completed=bool(r["is_completed"]), is_active=bool(r["is_active"]),
                created_at=Timestamp(r["created_at"]),
            )
            for r in rows
        ]

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM goals WHERE id = ?", (goal_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Goal(
            id=row["id"], name=row["name"], target_amount=Money(row["target_amount"], row["currency"], 2),
            currency=row["currency"], household_id=row["household_id"],
            target_date=Timestamp(row["target_date"]) if row["target_date"] else None,
            current_amount=Money(row["current_amount"], row["currency"], 2),
            is_completed=bool(row["is_completed"]), is_active=bool(row["is_active"]),
            created_at=Timestamp(row["created_at"]),
        )

    def update_goal(self, goal_id: str, updates: dict) -> Goal:
        conn = self._connect()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [goal_id]
        conn.execute(f"UPDATE goals SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return self.get_goal(goal_id)

    def delete_goal(self, goal_id: str, household_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM goals WHERE id = ? AND household_id = ?",
                     (goal_id, household_id))
        conn.commit()
        conn.close()

    # ── Assets ────────────────────────────

    def create_asset(self, asset: Asset) -> Asset:
        conn = self._connect()
        conn.execute(
            "INSERT INTO assets (id, name, value, currency, household_id, acquired_date, description, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (asset.id, asset.name, asset.value.value, asset.currency, asset.household_id,
             asset.acquired_date.to_iso(), asset.description, asset.notes,
             asset.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return asset

    def get_assets(self, household_id: str) -> List[Asset]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM assets WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Asset(
                id=r["id"], name=r["name"], value=Money(r["value"], r["currency"], 2),
                currency=r["currency"], household_id=r["household_id"],
                acquired_date=Timestamp(r["acquired_date"]),
                description=r["description"], notes=r["notes"],
                created_at=Timestamp(r["created_at"]),
            )
            for r in rows
        ]

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Asset(
            id=row["id"], name=row["name"], value=Money(row["value"], row["currency"], 2),
            currency=row["currency"], household_id=row["household_id"],
            acquired_date=Timestamp(row["acquired_date"]),
            description=row["description"], notes=row["notes"],
            created_at=Timestamp(row["created_at"]),
        )

    def update_asset(self, asset: Asset) -> Asset:
        conn = self._connect()
        conn.execute(
            "UPDATE assets SET name = ?, value = ?, currency = ?, acquired_date = ?, description = ?, notes = ? WHERE id = ?",
            (asset.name, asset.value.value, asset.currency, asset.acquired_date.to_iso(),
             asset.description, asset.notes, asset.id),
        )
        conn.commit()
        conn.close()
        return asset

    def delete_asset(self, asset_id: str, household_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM assets WHERE id = ? AND household_id = ?",
                     (asset_id, household_id))
        conn.commit()
        conn.close()

    # ── Liabilities ───────────────────────

    def create_liability(self, liability: Liability) -> Liability:
        conn = self._connect()
        conn.execute(
            "INSERT INTO liabilities (id, name, amount, currency, household_id, due_date, creditor, interest_rate, description, is_debt, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (liability.id, liability.name, liability.amount.value, liability.currency,
             liability.household_id, liability.due_date.to_iso(), liability.creditor,
             float(liability.interest_rate) if liability.interest_rate else None,
             liability.description, int(liability.is_debt), liability.created_at.to_iso()),
        )
        conn.commit()
        conn.close()
        return liability

    def get_liabilities(self, household_id: str) -> List[Liability]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM liabilities WHERE household_id = ?",
            (household_id,),
        ).fetchall()
        conn.close()
        return [
            Liability(
                id=r["id"], name=r["name"], amount=Money(r["amount"], r["currency"], 2),
                currency=r["currency"], household_id=r["household_id"],
                due_date=Timestamp(r["due_date"]), creditor=r["creditor"],
                interest_rate=Decimal(str(r["interest_rate"])) if r["interest_rate"] else None,
                description=r["description"], is_debt=bool(r["is_debt"]),
                created_at=Timestamp(r["created_at"]),
            )
            for r in rows
        ]

    def get_liability(self, liability_id: str) -> Optional[Liability]:
        conn = self._connect()
        row = conn.execute("SELECT * FROM liabilities WHERE id = ?", (liability_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return Liability(
            id=row["id"], name=row["name"], amount=Money(row["amount"], row["currency"], 2),
            currency=row["currency"], household_id=row["household_id"],
            due_date=Timestamp(row["due_date"]), creditor=row["creditor"],
            interest_rate=Decimal(str(row["interest_rate"])) if row["interest_rate"] else None,
            description=row["description"], is_debt=bool(row["is_debt"]),
            created_at=Timestamp(row["created_at"]),
        )

    def update_liability(self, liability: Liability) -> Liability:
        conn = self._connect()
        conn.execute(
            "UPDATE liabilities SET name = ?, amount = ?, currency = ?, due_date = ?, creditor = ?, interest_rate = ?, description = ?, is_debt = ? WHERE id = ?",
            (liability.name, liability.amount.value, liability.currency, liability.due_date.to_iso(),
             liability.creditor, float(liability.interest_rate) if liability.interest_rate else None,
             liability.description, int(liability.is_debt), liability.id),
        )
        conn.commit()
        conn.close()
        return liability

    def delete_liability(self, liability_id: str, household_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM liabilities WHERE id = ? AND household_id = ?",
                     (liability_id, household_id))
        conn.commit()
        conn.close()

    def create(self, obj):
        if isinstance(obj, Account):
            return self.create_account(obj)
        elif isinstance(obj, Member):
            return self.create_member(obj)
        elif isinstance(obj, Category):
            return self.create_category(obj)
        elif isinstance(obj, Transaction):
            return self.create_transaction(obj)
        elif isinstance(obj, Budget):
            return self.create_budget(obj)
        elif isinstance(obj, Debt):
            return self.create_debt(obj)
        elif isinstance(obj, Goal):
            return self.create_goal(obj)
        elif isinstance(obj, Asset):
            return self.create_asset(obj)
        elif isinstance(obj, Liability):
            return self.create_liability(obj)
        elif isinstance(obj, Household):
            return self.create_household(obj)
        elif isinstance(obj, User):
            return self.create_user(obj)
        elif isinstance(obj, Session):
            return self.create_session(obj)
        elif isinstance(obj, RecurringPayment):
            return self.create_recurring_payment(obj)
        elif isinstance(obj, DebtPayment):
            return self.create_debt_payment(obj)
        elif isinstance(obj, GoalContribution):
            return self.create_goal_contribution(obj)
        elif isinstance(obj, Transfer):
            return self.create_transfer(obj)
        elif isinstance(obj, LedgerEntry):
            return self.create_ledger_entry(obj)
        else:
            raise ValueError(f"Cannot create object of type {type(obj)}")

    def get_by_id(self, id: str):
        result = self.get_account(id)
        if result:
            return result
        result = self.get_member(id)
        if result:
            return result
        result = self.get_category(id)
        if result:
            return result
        result = self.get_budget(id)
        if result:
            return result
        result = self.get_debt(id)
        if result:
            return result
        result = self.get_goal(id)
        if result:
            return result
        result = self.get_asset(id)
        if result:
            return result
        result = self.get_liability(id)
        if result:
            return result
        result = self.get_user_by_id(id)
        if result:
            return result
        return None

    def get_by_household(self, household_id: str, type_hint=None):
        if type_hint == "account" or type_hint is None:
            accounts = self.get_accounts(household_id)
            if accounts:
                return accounts
        if type_hint == "member" or type_hint is None:
            members = self.get_members(household_id)
            if members:
                return members
        if type_hint == "category" or type_hint is None:
            categories = self.get_categories(household_id)
            if categories:
                return categories
        if type_hint == "budget" or type_hint is None:
            budgets = self.get_budgets(household_id)
            if budgets:
                return budgets
        if type_hint == "debt" or type_hint is None:
            debts = self.get_debts(household_id)
            if debts:
                return debts
        if type_hint == "goal" or type_hint is None:
            goals = self.get_goals(household_id)
            if goals:
                return goals
        if type_hint == "asset" or type_hint is None:
            assets = self.get_assets(household_id)
            if assets:
                return assets
        if type_hint == "liability" or type_hint is None:
            liabilities = self.get_liabilities(household_id)
            if liabilities:
                return liabilities
        return []

    def get_all(self):
        return self.get_households()

    def update(self, obj):
        if isinstance(obj, Household):
            return self.update_household(obj)
        elif isinstance(obj, Account):
            return self.update_account(obj)
        elif isinstance(obj, Member):
            return self.update_member(obj)
        elif isinstance(obj, Category):
            return self.update_category(obj)
        elif isinstance(obj, Asset):
            return self.update_asset(obj)
        elif isinstance(obj, Liability):
            return self.update_liability(obj)
        elif isinstance(obj, Debt):
            return self.update_debt(obj)
        elif isinstance(obj, Goal):
            return self.update_goal(obj)
        else:
            raise ValueError(f"Cannot update object of type {type(obj)}")

    def delete(self, id: str, household_id: str = None):
        self.delete_account(id, household_id)
        self.delete_member(id)
        self.delete_category(id)
        self.delete_budget(id, household_id)
        self.delete_debt(id, household_id)
        self.delete_goal(id, household_id)
        self.delete_asset(id, household_id)
        self.delete_liability(id, household_id)


# ── Repository initialization ────────────────────────────

init_db()

# ── Exports ───────────────────────────────────────────────

__all__ = [
    "SQLiteRepository",
    "init_db",
    "get_db_path",
    "get_connection",
]
