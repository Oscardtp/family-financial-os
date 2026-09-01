class DomainError(Exception):
    pass


class CurrencyMismatchError(DomainError):
    def __init__(self):
        super().__init__("Cannot operate on Money with different currencies")


class InsufficientFundsError(DomainError):
    def __init__(self, available: str, requested: str):
        super().__init__(f"Insufficient funds: available {available}, requested {requested}")


class InvalidAmountError(DomainError):
    def __init__(self, amount: str):
        super().__init__(f"Invalid monetary amount: {amount}")
