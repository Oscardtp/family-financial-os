from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.infrastructure.repositories.balance_history_repository import SQLAlchemyAccountBalanceHistoryRepository
from app.presentation.audit_helper import log_action


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tx_repo = SQLAlchemyTransactionRepository(db)
        self.account_repo = SQLAlchemyAccountRepository(db)
        self.category_repo = SQLAlchemyCategoryRepository(db)
        self.balance_history_repo = SQLAlchemyAccountBalanceHistoryRepository(db)

    async def list(
        self,
        household_id: str,
        account_id: str | None = None,
        category_id: str | None = None,
        date_from=None,
        date_to=None,
        skip: int = 0,
        limit: int = 100,
    ):
        return await self.tx_repo.get_all(
            household_id=household_id,
            account_id=account_id,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )

    async def create(self, data, user: dict) -> dict:
        household_id = user["household_id"]

        amount = Decimal(str(data.amount))
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        account = await self._get_owned_account(data.account_id, household_id)

        self._validate_transfer(data)
        await self._validate_category(data.category_id, data.type, household_id)

        if data.type == "transfer" and data.to_account_id:
            await self._get_owned_account(data.to_account_id, household_id)

        self._check_balance(account, data.type, amount)

        transaction = await self._register(
            account_id=data.account_id,
            category_id=data.category_id,
            user_id=user["id"],
            tx_type=data.type,
            amount=amount,
            description=data.description,
            tx_date=data.date,
            to_account_id=data.to_account_id,
            household_id=household_id,
            recurring_payment_id=None,
        )

        await log_action(
            self.db, household_id, user["id"], user["email"],
            "create", "transaction", transaction["id"], data.description,
        )
        return transaction

    async def execute_payment(
        self,
        *,
        account_id,
        amount,
        tx_type: str,
        tx_date,
        description: str | None = None,
        category_id=None,
        user_id: str,
        household_id: str,
        recurring_payment_id=None,
    ) -> dict:
        """Única entrada para persistir una salida real de dinero (D-5).

        Los ejecutores de pago (evento, ruta recurrente, process-due) resuelven
        el contexto y las reglas de dominio; la mutación persistente
        — Transaction + Account.balance + account_balance_history — vive aquí.

        Mismas validaciones que `create` (cuenta del hogar, categoría, fondos),
        sin lógica de transferencia porque un cobro nunca mueve dinero entre
        cuentas.
        """
        value = Decimal(str(amount))
        if value <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        account = await self._get_owned_account(account_id, household_id)
        await self._validate_category(category_id, tx_type, household_id)
        self._check_balance(account, tx_type, value)

        return await self._register(
            account_id=account_id,
            category_id=category_id,
            user_id=user_id,
            tx_type=tx_type,
            amount=value,
            description=description,
            tx_date=tx_date,
            to_account_id=None,
            household_id=household_id,
            recurring_payment_id=recurring_payment_id,
        )

    async def _register(
        self,
        *,
        account_id,
        category_id,
        user_id,
        tx_type: str,
        amount,
        description,
        tx_date,
        to_account_id=None,
        household_id: str | None = None,
        recurring_payment_id=None,
    ) -> dict:
        """Crea la Transaction y aplica el efecto monetario en una sola tanda."""
        transaction = await self.tx_repo.create({
            "household_id": household_id,
            "account_id": account_id,
            "category_id": category_id,
            "user_id": user_id,
            "type": tx_type,
            "amount": amount,
            "description": description,
            "date": tx_date,
            "to_account_id": to_account_id,
            "recurring_payment_id": recurring_payment_id,
        })

        await self._adjust_balances(
            tx_type, amount, account_id, to_account_id, transaction["id"]
        )
        return transaction

    async def delete(self, transaction_id: str, user: dict):
        transaction = await self.tx_repo.get_by_id(transaction_id)
        if not transaction:
            raise ValueError("Movimiento no encontrado")

        account = await self.account_repo.get_by_id(transaction["account_id"])
        if not account or account["household_id"] != user["household_id"]:
            raise ValueError("Movimiento no encontrado")

        await self._reverse_balances(transaction)

        await self.tx_repo.delete(transaction_id)
        await log_action(
            self.db, user["household_id"], user["id"], user["email"],
            "delete", "transaction", transaction_id, transaction.get("description"),
        )

    async def _get_owned_account(self, account_id: str, household_id: str) -> dict:
        account = await self.account_repo.get_by_id(account_id)
        if not account or account["household_id"] != household_id:
            raise ValueError("Cuenta no encontrada")
        return account

    def _validate_transfer(self, data):
        if data.type == "transfer" and not data.to_account_id:
            raise ValueError("Las transferencias necesitan una cuenta de destino")

        if data.type == "transfer" and data.to_account_id and data.account_id == data.to_account_id:
            raise ValueError("No puedes transferir a la misma cuenta")

    async def _validate_category(self, category_id, tx_type: str, household_id: str):
        if not category_id:
            return
        category = await self.category_repo.get_by_id(category_id)
        if not category or category.get("household_id") != household_id:
            raise ValueError("Categoría no encontrada")
        if category["type"] != tx_type:
            raise ValueError(
                f"La categoría '{category['name']}' es de tipo '{category['type']}', "
                f"pero estás intentando registrar un movimiento tipo '{tx_type}'. "
                f"Usa la categoría correcta."
            )

    def _check_balance(self, account: dict, tx_type: str, amount):
        if tx_type == "expense" and account["type"] != "credit_card":
            if account["balance"] < Decimal(str(amount)):
                raise ValueError(
                    f"No tienes suficiente plata. Disponible: ${account['balance']:,.2f}, "
                    f"necesitas: ${Decimal(str(amount)):,.2f}"
                )

        if tx_type == "transfer":
            if account["type"] != "credit_card" and account["balance"] < Decimal(str(amount)):
                raise ValueError(
                    f"No tienes suficiente plata en la cuenta origen. "
                    f"Disponible: ${account['balance']:,.2f}, necesitas: ${Decimal(str(amount)):,.2f}"
                )

    async def _adjust_balances(
        self, tx_type: str, amount, account_id, to_account_id, transaction_id: str | None = None
    ):
        amount = Decimal(str(amount))

        if tx_type == "income":
            account = await self.account_repo.get_by_id(account_id)
            balance_before = account["balance"]
            await self.account_repo.update_balance(account_id, amount)
            account_after = await self.account_repo.get_by_id(account_id)
            await self._record_balance_history(
                account_id, transaction_id, balance_before,
                account_after["balance"], amount, "income"
            )

        elif tx_type == "expense":
            account = await self.account_repo.get_by_id(account_id)
            balance_before = account["balance"]
            deducted = await self.account_repo.deduct_balance(account_id, amount)
            if not deducted:
                raise ValueError("No tienes suficiente plata para este pago")
            account_after = await self.account_repo.get_by_id(account_id)
            await self._record_balance_history(
                account_id, transaction_id, balance_before,
                account_after["balance"], -amount, "expense"
            )

        elif tx_type == "transfer" and to_account_id:
            # Origen
            account_from = await self.account_repo.get_by_id(account_id)
            balance_before_from = account_from["balance"]
            deducted = await self.account_repo.deduct_balance(account_id, amount)
            if not deducted:
                raise ValueError("No tienes suficiente plata en la cuenta origen")
            account_after_from = await self.account_repo.get_by_id(account_id)
            await self._record_balance_history(
                account_id, transaction_id, balance_before_from,
                account_after_from["balance"], -amount, "transfer"
            )

            # Destino
            account_to = await self.account_repo.get_by_id(to_account_id)
            balance_before_to = account_to["balance"]
            await self.account_repo.update_balance(to_account_id, amount)
            account_after_to = await self.account_repo.get_by_id(to_account_id)
            await self._record_balance_history(
                to_account_id, transaction_id, balance_before_to,
                account_after_to["balance"], amount, "transfer"
            )

    async def _record_balance_history(
        self, account_id: str, transaction_id: str | None,
        balance_before: Decimal, balance_after: Decimal,
        change_amount: Decimal, change_type: str
    ):
        await self.balance_history_repo.create({
            "account_id": account_id,
            "transaction_id": transaction_id,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "change_amount": change_amount,
            "change_type": change_type,
        })

    async def _reverse_balances(self, transaction: dict):
        amount = transaction["amount"]
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))

        if transaction["type"] == "income":
            account = await self.account_repo.get_by_id(transaction["account_id"])
            balance_before = account["balance"]
            await self.account_repo.update_balance(transaction["account_id"], -amount)
            account_after = await self.account_repo.get_by_id(transaction["account_id"])
            await self._record_balance_history(
                transaction["account_id"], transaction["id"], balance_before,
                account_after["balance"], -amount, "adjustment"
            )
        elif transaction["type"] == "expense":
            account = await self.account_repo.get_by_id(transaction["account_id"])
            balance_before = account["balance"]
            await self.account_repo.update_balance(transaction["account_id"], amount)
            account_after = await self.account_repo.get_by_id(transaction["account_id"])
            await self._record_balance_history(
                transaction["account_id"], transaction["id"], balance_before,
                account_after["balance"], amount, "adjustment"
            )
        elif transaction["type"] == "transfer" and transaction.get("to_account_id"):
            # Revertir destino
            account_to = await self.account_repo.get_by_id(transaction["to_account_id"])
            balance_before_to = account_to["balance"]
            await self.account_repo.update_balance(transaction["to_account_id"], -amount)
            account_after_to = await self.account_repo.get_by_id(transaction["to_account_id"])
            await self._record_balance_history(
                transaction["to_account_id"], transaction["id"], balance_before_to,
                account_after_to["balance"], -amount, "adjustment"
            )
            # Revertir origen
            account_from = await self.account_repo.get_by_id(transaction["account_id"])
            balance_before_from = account_from["balance"]
            await self.account_repo.update_balance(transaction["account_id"], amount)
            account_after_from = await self.account_repo.get_by_id(transaction["account_id"])
            await self._record_balance_history(
                transaction["account_id"], transaction["id"], balance_before_from,
                account_after_from["balance"], amount, "adjustment"
            )
