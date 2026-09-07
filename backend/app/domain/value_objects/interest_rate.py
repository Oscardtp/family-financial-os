from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum


class RateType(str, Enum):
    EA = "EA"
    EM = "EM"
    NOMINAL = "nominal"
    DAILY = "daily"


@dataclass(frozen=True)
class InterestRate:
    value: Decimal
    rate_type: RateType = RateType.EA

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            try:
                object.__setattr__(self, "value", Decimal(str(self.value)))
            except (InvalidOperation, ValueError):
                raise InvalidOperation(f"Invalid interest rate value: {self.value}")
