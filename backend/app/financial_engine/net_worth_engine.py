from dataclasses import dataclass
from decimal import Decimal
from app.domain.value_objects.money import Money
from app.financial_engine.money_operations import MoneyOperations


@dataclass
class NetWorthResult:
    total_assets: Money
    total_liabilities: Money
    net_worth: Money
    assets_detail: list[dict]
    liabilities_detail: list[dict]


class NetWorthEngine:
    def calculate_net_worth(
        self,
        assets: list[dict],
        liabilities: list[dict],
        account_balances: list[dict] | None = None,
    ) -> NetWorthResult:
        total_assets = Money.zero()
        total_liabilities = Money.zero()

        assets_detail = []
        for asset in assets:
            value = Money(Decimal(str(asset["value"])))
            total_assets = total_assets + value
            assets_detail.append({
                "id": str(asset["id"]),
                "name": asset["name"],
                "type": asset["type"],
                "value": value,
            })

        if account_balances:
            for account in account_balances:
                balance = Money(Decimal(str(account["balance"])))
                if balance.is_positive():
                    total_assets = total_assets + balance
                    assets_detail.append({
                        "id": str(account["id"]),
                        "name": account["name"],
                        "type": f"account_{account['type']}",
                        "value": balance,
                    })

        liabilities_detail = []
        for liability in liabilities:
            balance = Money(Decimal(str(liability["current_balance"])))
            total_liabilities = total_liabilities + balance
            liabilities_detail.append({
                "id": str(liability["id"]),
                "name": liability["name"],
                "type": liability["type"],
                "balance": balance,
            })

        return NetWorthResult(
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=total_assets - total_liabilities,
            assets_detail=assets_detail,
            liabilities_detail=liabilities_detail,
        )
