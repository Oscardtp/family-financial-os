from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.presentation.audit_helper import log_action


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tx_repo = SQLAlchemyTransactionRepository(db)
        self.account_repo = SQLAlchemyAccountRepository(db)
        self.category_repo = SQLAlchemyCategoryRepository(db)

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

        account = await self._get_owned_account(data.account_id, household_id)

        self._validate_transfer(data)
        await self._validate_category(data, household_id)

        if data.type == "transfer" and data.to_account_id:
            await self._get_owned_account(data.to_account_id, household_id)

        self._check_balance(account, data.type, data.amount)

        await self._adjust_balances(data)

        transaction = await self.tx_repo.create({
            "account_id": data.account_id,
            "category_id": data.category_id,
            "user_id": user["id"],
            "type": data.type,
            "amount": Decimal(str(data.amount)),
            "description": data.description,
            "date": data.date,
            "to_account_id": data.to_account_id,
        })

        await log_action(
            self.db, household_id, user["id"], user["email"],
            "create", "transaction", transaction["id"], data.description,
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

    async def _validate_category(self, data, household_id: str):
        if not data.category_id:
            return
        category = await self.category_repo.get_by_id(data.category_id)
        if not category or category.get("household_id") != household_id:
            raise ValueError("Categoría no encontrada")
        if category["type"] != data.type:
            raise ValueError(
                f"La categoría '{category['name']}' es de tipo '{category['type']}', "
                f"pero estás intentando registrar un movimiento tipo '{data.type}'. "
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

    async def _adjust_balances(self, data):
        amount = Decimal(str(data.amount))

        if data.type == "income":
            await self.account_repo.update_balance(data.account_id, amount)

        elif data.type == "expense":
            deducted = await self.account_repo.deduct_balance(data.account_id, amount)
            if not deducted:
                raise ValueError("No tienes suficiente plata para este pago")

        elif data.type == "transfer" and data.to_account_id:
            deducted = await self.account_repo.deduct_balance(data.account_id, amount)
            if not deducted:
                raise ValueError("No tienes suficiente plata en la cuenta origen")
            await self.account_repo.update_balance(data.to_account_id, amount)

    async def _reverse_balances(self, transaction: dict):
        amount = transaction["amount"]
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))

        if transaction["type"] == "income":
            await self.account_repo.update_balance(transaction["account_id"], -amount)
        elif transaction["type"] == "expense":
            await self.account_repo.update_balance(transaction["account_id"], amount)
        elif transaction["type"] == "transfer" and transaction.get("to_account_id"):
            await self.account_repo.update_balance(transaction["account_id"], amount)
            await self.account_repo.update_balance(transaction["to_account_id"], -amount)
