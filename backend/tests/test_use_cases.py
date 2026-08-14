"""Tests for use case domain invariants."""

from __future__ import annotations
import pytest
from unittest.mock import MagicMock
from decimal import Decimal

from app.domain.domain import (
    Money, Timestamp, Account, AccountType, Transaction,
    TransactionType, TransactionStatus, Budget, Debt, Goal,
    Asset, Liability, Member, Household, Transfer, LedgerEntry
)
from app.application.use_cases import TransactionUseCase, AccountUseCase, BudgetUseCase


# ── TransactionUseCase invariants ─────────────

def test_register_expense_insufficient_balance():
    mock_tx_repo = MagicMock()
    mock_acc_repo = MagicMock()
    mock_transfer_repo = MagicMock()
    mock_ledger_repo = MagicMock()

    account = Account(id="acc-1", name="Test", account_type=AccountType.CASH, currency="COP", household_id="h", balance=Money(5000, "COP", 2))
    mock_acc_repo.get_by_id.return_value = account

    uc = TransactionUseCase(mock_tx_repo, mock_acc_repo, mock_transfer_repo, mock_ledger_repo)

    with pytest.raises(ValueError, match="Insufficient balance"):
        uc.register_expense("h", "acc-1", 100.0, "cat-1", "Test expense")


def test_register_transfer_same_account_raises():
    mock_tx_repo = MagicMock()
    mock_acc_repo = MagicMock()
    mock_transfer_repo = MagicMock()
    mock_ledger_repo = MagicMock()

    account = Account(id="acc-1", name="Test", account_type=AccountType.CASH, currency="COP", household_id="h", balance=Money(10000, "COP", 2))
    mock_acc_repo.get_by_id.return_value = account

    uc = TransactionUseCase(mock_tx_repo, mock_acc_repo, mock_transfer_repo, mock_ledger_repo)

    with pytest.raises(ValueError, match="Cannot transfer to same account"):
        uc.register_transfer("h", "acc-1", "acc-1", 100.0, "Test transfer")


def test_register_transfer_insufficient_balance():
    mock_tx_repo = MagicMock()
    mock_acc_repo = MagicMock()
    mock_transfer_repo = MagicMock()
    mock_ledger_repo = MagicMock()

    from_account = Account(id="acc-1", name="From", account_type=AccountType.CASH, currency="COP", household_id="h", balance=Money(5000, "COP", 2))
    to_account = Account(id="acc-2", name="To", account_type=AccountType.BANK, currency="COP", household_id="h", balance=Money(0, "COP", 2))
    mock_acc_repo.get_by_id.side_effect = lambda id: from_account if id == "acc-1" else to_account

    uc = TransactionUseCase(mock_tx_repo, mock_acc_repo, mock_transfer_repo, mock_ledger_repo)

    with pytest.raises(ValueError, match="Insufficient balance"):
        uc.register_transfer("h", "acc-1", "acc-2", 10000.0, "Test transfer")


def test_register_income_positive_amount():
    mock_tx_repo = MagicMock()
    mock_acc_repo = MagicMock()
    mock_transfer_repo = MagicMock()
    mock_ledger_repo = MagicMock()

    account = Account(id="acc-1", name="Test", account_type=AccountType.CASH, currency="COP", household_id="h", balance=Money(5000, "COP", 2))
    mock_acc_repo.get_by_id.return_value = account

    uc = TransactionUseCase(mock_tx_repo, mock_acc_repo, mock_transfer_repo, mock_ledger_repo)

    with pytest.raises(ValueError, match="Cannot represent negative money"):
        uc.register_income("h", "acc-1", -100.0, "cat-1", "Test income")


def test_register_expense_positive_amount():
    mock_tx_repo = MagicMock()
    mock_acc_repo = MagicMock()
    mock_transfer_repo = MagicMock()
    mock_ledger_repo = MagicMock()

    account = Account(id="acc-1", name="Test", account_type=AccountType.CASH, currency="COP", household_id="h", balance=Money(10000, "COP", 2))
    mock_acc_repo.get_by_id.return_value = account

    uc = TransactionUseCase(mock_tx_repo, mock_acc_repo, mock_transfer_repo, mock_ledger_repo)

    with pytest.raises(ValueError, match="Cannot represent negative money"):
        uc.register_expense("h", "acc-1", -100.0, "cat-1", "Test expense")


# ── AccountUseCase invariants ────────────────

def test_create_account_with_negative_balance_raises():
    mock_acc_repo = MagicMock()

    uc = AccountUseCase(mock_acc_repo)

    with pytest.raises(ValueError, match="Cannot represent negative money"):
        uc.create_account("h", "Test", AccountType.CASH, "COP", -100.0)


# ── BudgetUseCase invariants ──────────────────

def test_create_budget_with_negative_amount_raises():
    mock_budget_repo = MagicMock()

    uc = BudgetUseCase(mock_budget_repo)

    with pytest.raises(ValueError, match="Cannot represent negative money"):
        uc.create_budget("h", "cat-1", -1000.0, "monthly", 2026)
