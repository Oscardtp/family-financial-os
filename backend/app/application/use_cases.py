"""Application layer with use cases for Family Financial OS."""

from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from app.domain.domain import (
    Money, Timestamp, Account, AccountType, Transaction,
    TransactionType, TransactionStatus, Budget, Debt, Goal,
    Asset, Liability, Member, Household, User, Session,
    Transfer, LedgerEntry, RecurringPayment, DebtPayment, GoalContribution,
    Category, Notification
)
from app.financial_engine.engine import (
    cash_flow, savings_rate, net_worth, debt_balance,
    goal_progress, monthly_projection, apply_discount,
    apply_tax, round_to_scale, budget_status, debt_payoff_status,
    transfer_amount
)
from app.application.interfaces import (
    HouseholdRepository, MemberRepository, AccountRepository,
    CategoryRepository, TransactionRepository, TransferRepository,
    LedgerEntryRepository, BudgetRepository, RecurringPaymentRepository,
    DebtRepository, DebtPaymentRepository, GoalRepository,
    GoalContributionRepository, AssetRepository, LiabilityRepository
)


class TransactionUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
        transfer_repo: TransferRepository,
        ledger_repo: LedgerEntryRepository,
        budget_repo: BudgetRepository = None,
    ):
        self._transaction_repo = transaction_repo
        self._account_repo = account_repo
        self._transfer_repo = transfer_repo
        self._ledger_repo = ledger_repo
        self._budget_repo = budget_repo

    def register_income(self, household_id: str, account_id: str, amount: float, category_id: str, description: str) -> Transaction:
        account = self._account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        money_amount = Money.from_float(amount, account.currency, 2)
        new_balance = account.balance + money_amount

        transaction = Transaction(
            account_id=account_id,
            category_id=category_id,
            type=TransactionType.INCOME,
            amount=money_amount,
            description=description,
            date=Timestamp(datetime.now()),
            household_id=household_id,
            status=TransactionStatus.PROCESSED,
        )
        self._transaction_repo.create(transaction)
        self._account_repo.update_balance(account_id, new_balance)
        self._ledger_repo.create(LedgerEntry(
            transaction_id=transaction.id,
            account_id=account_id,
            type=TransactionType.INCOME,
            amount=money_amount,
            balance_before=account.balance,
            balance_after=new_balance,
            household_id=household_id,
        ))
        return transaction

    def register_expense(self, household_id: str, account_id: str, amount: float, category_id: str, description: str) -> Transaction:
        account = self._account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        money_amount = Money.from_float(amount, account.currency, 2)
        if account.balance < money_amount:
            raise ValueError("Insufficient balance")

        new_balance = account.balance - money_amount

        transaction = Transaction(
            account_id=account_id,
            category_id=category_id,
            type=TransactionType.EXPENSE,
            amount=money_amount,
            description=description,
            date=Timestamp(datetime.now()),
            household_id=household_id,
            status=TransactionStatus.PROCESSED,
        )
        self._transaction_repo.create(transaction)
        self._account_repo.update_balance(account_id, new_balance)
        self._ledger_repo.create(LedgerEntry(
            transaction_id=transaction.id,
            account_id=account_id,
            type=TransactionType.EXPENSE,
            amount=money_amount,
            balance_before=account.balance,
            balance_after=new_balance,
            household_id=household_id,
        ))

        if self._budget_repo and category_id:
            budgets = self._budget_repo.get_budgets(household_id)
            for budget in budgets:
                if budget.category_id == category_id:
                    new_spent = budget.spent + money_amount
                    self._budget_repo.update(budget.id, {"spent": new_spent.value})
                    break

        return transaction

    def register_transfer(self, household_id: str, from_account_id: str, to_account_id: str, amount: float, description: str = "") -> Transfer:
        from_account = self._account_repo.get_by_id(from_account_id)
        to_account = self._account_repo.get_by_id(to_account_id)
        if not from_account or not to_account:
            raise ValueError("Account not found")
        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to same account")

        money_amount = Money.from_float(amount, from_account.currency, 2)
        if from_account.balance < money_amount:
            raise ValueError("Insufficient balance")

        new_from_balance = from_account.balance - money_amount
        new_to_balance = to_account.balance + money_amount

        transfer = Transfer(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=money_amount,
            date=Timestamp(datetime.now()),
            household_id=household_id,
            description=description,
        )
        self._transfer_repo.create(transfer)

        self._account_repo.update_balance(from_account_id, new_from_balance)
        self._account_repo.update_balance(to_account_id, new_to_balance)

        self._ledger_repo.create(LedgerEntry(
            transaction_id=transfer.id,
            account_id=from_account_id,
            type="transfer_out",
            amount=money_amount,
            balance_before=from_account.balance,
            balance_after=new_from_balance,
            household_id=household_id,
        ))
        self._ledger_repo.create(LedgerEntry(
            transaction_id=transfer.id,
            account_id=to_account_id,
            type="transfer_in",
            amount=money_amount,
            balance_before=to_account.balance,
            balance_after=new_to_balance,
            household_id=household_id,
        ))

        return transfer

    def get_transactions(self, household_id: str) -> List[Transaction]:
        return self._transaction_repo.get_by_household(household_id)

    def get_transactions_by_account(self, account_id: str) -> List[Transaction]:
        return self._transaction_repo.get_by_account(account_id)

    def get_balance(self, account_id: str) -> Optional[Money]:
        return self._account_repo.get_balance(account_id)

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        return self._transaction_repo.get_by_id(transaction_id)

    def get_accounts(self, household_id: str) -> List[Account]:
        return self._account_repo.get_by_household(household_id)

    def update_transaction(self, transaction: Transaction) -> Transaction:
        return self._transaction_repo.update(transaction)

    def delete_transaction(self, transaction_id: str, household_id: str) -> None:
        self._transaction_repo.delete(transaction_id, household_id)


class BudgetUseCase:
    def __init__(self, repo: BudgetRepository):
        self._repo = repo

    def create_budget(self, household_id: str, category_id: str, limit: float, period: str = "monthly", year: int = None) -> Budget:
        budget = Budget(
            id=str(uuid.uuid4()),
            household_id=household_id,
            category_id=category_id,
            amount=Money.from_float(limit, "COP", 2),
            period=period,
            year=year or datetime.now().year,
        )
        self._repo.create(budget)
        return budget

    def get_budgets(self, household_id: str) -> List[Budget]:
        return self._repo.get_by_household(household_id)

    def get_budget(self, budget_id: str) -> Optional[Budget]:
        return self._repo.get_by_id(budget_id)

    def get_budget_status(self, budget: Budget, actual_spend: Money) -> str:
        return budget_status(budget, actual_spend)

    def update_budget_limit(self, budget_id: str, new_limit: float) -> Budget:
        return self._repo.update(budget_id, {"amount": Money.from_float(new_limit, "COP", 2).value})


class DebtUseCase:
    def __init__(
        self,
        repo: DebtRepository,
        payment_repo: DebtPaymentRepository,
        account_repo: AccountRepository,
        ledger_repo: LedgerEntryRepository,
    ):
        self._repo = repo
        self._payment_repo = payment_repo
        self._account_repo = account_repo
        self._ledger_repo = ledger_repo

    def create_debt(self, household_id: str, name: str, principal: float, rate: float, monthly_payment: float, currency: str, due_date: str, creditor: str = None, installments: int = None) -> Debt:
        debt = Debt(
            id=str(uuid.uuid4()),
            name=name,
            principal=Money.from_float(principal, currency, 2),
            interest_rate=Decimal(str(rate)),
            monthly_payment=Money.from_float(monthly_payment, currency, 2),
            currency=currency,
            due_date=Timestamp(due_date),
            household_id=household_id,
            creditor=creditor,
            installments=installments,
        )
        self._repo.create(debt)
        return debt

    def get_debts(self, household_id: str) -> List[Debt]:
        return self._repo.get_by_household(household_id)

    def get_debt(self, debt_id: str) -> Optional[Debt]:
        return self._repo.get_by_id(debt_id)

    def make_payment(self, debt_id: str, payment_amount: float, account_id: str, household_id: str, notes: str = "") -> DebtPayment:
        debt = self._repo.get_by_id(debt_id)
        if not debt:
            raise ValueError("Debt not found")

        account = self._account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        money_payment = Money.from_float(payment_amount, debt.currency, 2)
        if account.balance < money_payment:
            raise ValueError("Insufficient balance")

        new_debt_balance = debt.balance - money_payment
        new_account_balance = account.balance - money_payment

        self._repo.update(debt_id, {"balance": new_debt_balance.value})

        payment = DebtPayment(
            debt_id=debt_id,
            amount=money_payment,
            date=Timestamp(datetime.now()),
            household_id=household_id,
            account_id=account_id,
            notes=notes,
        )
        self._payment_repo.create(payment)

        self._account_repo.update_balance(account_id, new_account_balance)
        self._ledger_repo.create(LedgerEntry(
            transaction_id=payment.id,
            account_id=account_id,
            type="debt_payment",
            amount=money_payment,
            balance_before=account.balance,
            balance_after=new_account_balance,
            household_id=household_id,
        ))

        return payment


class GoalUseCase:
    def __init__(
        self,
        repo: GoalRepository,
        contribution_repo: GoalContributionRepository,
        account_repo: AccountRepository,
        ledger_repo: LedgerEntryRepository,
    ):
        self._repo = repo
        self._contribution_repo = contribution_repo
        self._account_repo = account_repo
        self._ledger_repo = ledger_repo

    def create_goal(self, household_id: str, name: str, target_amount: float, currency: str = "COP", target_date: str = None) -> Goal:
        goal = Goal(
            id=str(uuid.uuid4()),
            name=name,
            target_amount=Money.from_float(target_amount, currency, 2),
            household_id=household_id,
            currency=currency,
            target_date=Timestamp(target_date) if target_date else None,
        )
        self._repo.create(goal)
        return goal

    def get_goals(self, household_id: str) -> List[Goal]:
        return self._repo.get_by_household(household_id)

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self._repo.get_by_id(goal_id)

    def contribute(self, goal_id: str, amount: float, account_id: str, household_id: str, notes: str = "") -> GoalContribution:
        goal = self._repo.get_by_id(goal_id)
        if not goal:
            raise ValueError("Goal not found")

        account = self._account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        money_amount = Money.from_float(amount, goal.currency, 2)
        if account.balance < money_amount:
            raise ValueError("Insufficient balance")

        new_current = goal.current_amount + money_amount
        new_account_balance = account.balance - money_amount

        self._repo.update(goal_id, {"current_amount": new_current.value})

        contribution = GoalContribution(
            goal_id=goal_id,
            amount=money_amount,
            date=Timestamp(datetime.now()),
            household_id=household_id,
            account_id=account_id,
            notes=notes,
        )
        self._contribution_repo.create(contribution)

        self._account_repo.update_balance(account_id, new_account_balance)
        self._ledger_repo.create(LedgerEntry(
            transaction_id=contribution.id,
            account_id=account_id,
            type="goal_contribution",
            amount=money_amount,
            balance_before=account.balance,
            balance_after=new_account_balance,
            household_id=household_id,
        ))

        return contribution

    def update_goal_progress(self, goal_id: str, amount: float) -> Goal:
        return self._repo.update(goal_id, {"current_amount": Money.from_float(amount, "COP", 2).value})

    def delete_goal(self, goal_id: str, household_id: str) -> None:
        self._repo.delete(goal_id, household_id)


class AccountUseCase:
    def __init__(self, repo: AccountRepository):
        self._repo = repo

    def create_account(self, household_id: str, name: str, account_type: str, currency: str, balance: float, member_id: str = None) -> Account:
        account = Account(
            id=str(uuid.uuid4()),
            name=name,
            account_type=account_type,
            currency=currency,
            balance=Money.from_float(balance, currency, 2),
            household_id=household_id,
            member_id=member_id,
        )
        self._repo.create(account)
        return account

    def get_accounts(self, household_id: str) -> List[Account]:
        return self._repo.get_by_household(household_id)

    def get_account(self, account_id: str) -> Optional[Account]:
        return self._repo.get_by_id(account_id)

    def update_account_balance(self, account_id: str, new_balance: float) -> None:
        money_balance = Money.from_float(new_balance, "COP", 2)
        self._repo.update_balance(account_id, money_balance)

    def delete_account(self, account_id: str, household_id: str) -> None:
        self._repo.delete(account_id, household_id)


class AssetUseCase:
    def __init__(self, repo: AssetRepository):
        self._repo = repo

    def create_asset(self, household_id: str, name: str, value: float, currency: str, acquired_date: str, description: str = None, notes: str = None) -> Asset:
        asset = Asset(
            id=str(uuid.uuid4()),
            name=name,
            value=Money.from_float(value, currency, 2),
            currency=currency,
            household_id=household_id,
            acquired_date=Timestamp(acquired_date),
            description=description,
            notes=notes,
        )
        self._repo.create(asset)
        return asset

    def get_assets(self, household_id: str) -> List[Asset]:
        return self._repo.get_by_household(household_id)

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        return self._repo.get_by_id(asset_id)


class LiabilityUseCase:
    def __init__(self, repo: LiabilityRepository):
        self._repo = repo

    def create_liability(self, household_id: str, name: str, amount: float, currency: str, due_date: str, creditor: str = None, interest_rate: float = None, description: str = None) -> Liability:
        liability = Liability(
            id=str(uuid.uuid4()),
            name=name,
            amount=Money.from_float(amount, currency, 2),
            currency=currency,
            household_id=household_id,
            due_date=Timestamp(due_date),
            creditor=creditor,
            interest_rate=Decimal(str(interest_rate)) if interest_rate else None,
            description=description,
        )
        self._repo.create(liability)
        return liability

    def get_liabilities(self, household_id: str) -> List[Liability]:
        return self._repo.get_by_household(household_id)

    def get_liability(self, liability_id: str) -> Optional[Liability]:
        return self._repo.get_by_id(liability_id)

    def delete_liability(self, liability_id: str, household_id: str) -> None:
        self._repo.delete(liability_id, household_id)


class MemberUseCase:
    def __init__(self, repo: MemberRepository):
        self._repo = repo

    def create_member(self, household_id: str, name: str, role: str = "adult", email: str = None) -> Member:
        member = Member(
            id=str(uuid.uuid4()),
            name=name,
            household_id=household_id,
            role=role,
            email=email,
        )
        self._repo.create(member)
        return member

    def get_members(self, household_id: str) -> List[Member]:
        return self._repo.get_by_household(household_id)

    def get_member(self, member_id: str) -> Optional[Member]:
        return self._repo.get_by_id(member_id)

    def update_member_role(self, member_id: str, new_role: str) -> Member:
        # For simplicity, we'll implement a basic update
        # In a real app, this would be in the repository
        member = self._repo.get_by_id(member_id)
        if member:
            member.role = new_role
        return member


class HouseholdUseCase:
    def __init__(self, repo: HouseholdRepository):
        self._repo = repo

    def create_household(self, name: str, country: str = "CO", currency: str = "COP", timezone: str = "America/Bogota") -> Household:
        household = Household(
            id=str(uuid.uuid4()),
            name=name,
            country=country,
            currency=currency,
            timezone=timezone,
        )
        self._repo.create(household)
        return household

    def get_household(self, household_id: str) -> Optional[Household]:
        return self._repo.get_by_id(household_id)

    def get_households(self) -> List[Household]:
        return self._repo.get_all()


class CategoryUseCase:
    def __init__(self, repo: CategoryRepository):
        self._repo = repo

    def create_category(self, household_id: str, name: str, type: str, parent_id: str = None, color: str = None, icon: str = None) -> Category:
        category = Category(
            id=str(uuid.uuid4()),
            name=name,
            type=type,
            household_id=household_id,
            parent_id=parent_id,
            color=color,
            icon=icon,
        )
        self._repo.create(category)
        return category

    def get_categories(self, household_id: str) -> List[Category]:
        return self._repo.get_by_household(household_id)

    def get_category(self, category_id: str) -> Optional[Category]:
        return self._repo.get_by_id(category_id)


class RecurringPaymentUseCase:
    def __init__(self, repo):
        self._repo = repo

    def create_recurring_payment(self, household_id: str, name: str, amount: float, frequency: str, category_id: str, account_id: str, day_of_month: int = None, next_due_date: str = None) -> RecurringPayment:
        payment = RecurringPayment(
            id=str(uuid.uuid4()),
            name=name,
            amount=Money.from_float(amount, "COP", 2),
            frequency=frequency,
            category_id=category_id,
            account_id=account_id,
            household_id=household_id,
            day_of_month=day_of_month,
            next_due_date=Timestamp(next_due_date) if next_due_date else Timestamp(datetime.now()),
        )
        self._repo.create(payment)
        return payment

    def get_recurring_payments(self, household_id: str) -> List[RecurringPayment]:
        return self._repo.get_by_household(household_id, type_hint="recurring_payment")

    def get_recurring_payment(self, payment_id: str) -> Optional[RecurringPayment]:
        return self._repo.get_by_id(payment_id)

    def execute_recurring_payment(self, payment_id: str, household_id: str) -> Transaction:
        payment = self._repo.get_by_id(payment_id)
        if not payment:
            raise ValueError("Recurring payment not found")
        if not payment.is_active:
            raise ValueError("Recurring payment is not active")

        account = self._repo.get_account(payment.account_id)
        if not account:
            raise ValueError("Account not found")

        money_amount = payment.amount
        if account.balance < money_amount:
            raise ValueError("Insufficient balance")

        new_balance = account.balance - money_amount

        transaction = Transaction(
            account_id=payment.account_id,
            category_id=payment.category_id,
            type=TransactionType.EXPENSE,
            amount=money_amount,
            description=f"Pago recurrente: {payment.name}",
            date=Timestamp(datetime.now()),
            household_id=household_id,
            status=TransactionStatus.PROCESSED,
        )
        self._repo.create(transaction)
        self._repo.update_balance(payment.account_id, new_balance)
        self._repo.create(LedgerEntry(
            transaction_id=transaction.id,
            account_id=payment.account_id,
            type=TransactionType.EXPENSE,
            amount=money_amount,
            balance_before=account.balance,
            balance_after=new_balance,
            household_id=household_id,
        ))

        payment.next_due_date = Timestamp(self._calculate_next_due(payment.next_due_date.to_datetime(), payment.frequency))
        self._repo.update(payment.id, {
            "next_due_date": payment.next_due_date.to_iso(),
        })

        return transaction

    def skip_recurring_payment(self, payment_id: str) -> RecurringPayment:
        payment = self._repo.get_by_id(payment_id)
        if not payment:
            raise ValueError("Recurring payment not found")

        payment.next_due_date = Timestamp(self._calculate_next_due(payment.next_due_date.to_datetime(), payment.frequency))
        self._repo.update(payment.id, {
            "next_due_date": payment.next_due_date.to_iso(),
        })
        return payment

    def _calculate_next_due(self, current_date, frequency: str):
        if frequency == "monthly":
            month = current_date.month - 1 + 1
            year = current_date.year + month // 12
            month = month % 12 + 1
            day = min(current_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
            return datetime(year, month, day, current_date.hour, current_date.minute, current_date.second)
        elif frequency == "weekly":
            return current_date + timedelta(days=7)
        elif frequency == "biweekly":
            return current_date + timedelta(days=14)
        elif frequency == "yearly":
            return current_date.replace(year=current_date.year + 1)
        else:
            return current_date + timedelta(days=30)


class AuthUseCase:
    def __init__(self, repo: SQLiteRepository):
        self._repo = repo

    def register(self, name: str, email: str, password_hash: str, household_name: str = "Mi Hogar") -> tuple[User, Household]:
        existing = self._repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        household = Household(
            id=str(uuid.uuid4()),
            name=household_name,
        )
        self._repo.create_household(household)

        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            password_hash=password_hash,
            household_id=household.id,
        )
        self._repo.create_user(user)
        return user, household

    def login(self, email: str, password_hash: str) -> tuple[User, Session]:
        user = self._repo.get_by_email(email)
        if not user or not user.is_active:
            raise ValueError("Invalid credentials")

        session = Session(
            id=str(uuid.uuid4()),
            user_id=user.id,
            household_id=user.household_id or "default-household",
            expires_at=Timestamp((datetime.now() + timedelta(days=7)).isoformat()),
        )
        self._repo.create_session(session)
        return user, session

    def logout(self, session_id: str) -> None:
        self._repo.delete_session(session_id)

    def get_current_user(self, session_id: str) -> Optional[tuple[User, Session]]:
        session = self._repo.get_session(session_id)
        if not session or not session.is_active:
            return None
        user = self._repo.get_user_by_id(session.user_id)
        if not user or not user.is_active:
            return None
        return user, session
