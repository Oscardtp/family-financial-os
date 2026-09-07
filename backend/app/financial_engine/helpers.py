from datetime import date
from decimal import Decimal


def months_between(start: date, end: date) -> int:
    total = (end.year - start.year) * 12 + (end.month - start.month)
    return max(total, 0)
