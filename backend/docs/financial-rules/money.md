# Money Value Object — Financial Rules

## 1. Internal Representation

All monetary values are stored as **integers in the smallest currency unit** (centavos for COP).

| Property | Type | Description |
|----------|------|-------------|
| `value` | `int` | Amount in centavos (1 COP = 100 centavos) |
| `currency` | `str` | ISO 4217 code (e.g., `"COP"`) |
| `scale` | `int` | Number of decimal places (default: `2`) |

## 2. Creation

```python
Money(100000, "COP", 2)           # 1,000.00 COP from integer
Money.from_float(12.34, "COP")    # 12.34 COP from float
Money.from_decimal(Decimal("10"), "COP")  # 10.00 COP from Decimal
Money.from_string("99.99", "COP") # 99.99 COP from string
```

### Validation
- **Negative amounts are prohibited.** `Money(-1, "COP", 2)` raises `ValueError`.

## 3. Arithmetic Operations

| Operation | Behavior |
|-----------|----------|
| `a + b` | Addition. Raises `ValueError` if currencies differ. |
| `a - b` | Subtraction. Raises `ValueError` if currencies differ. Result may be negative at the value level, but `Money` constructor rejects negative values. |
| `a * factor` | Multiplication by `int`, `float`, or `Decimal`. Result is always rounded toward zero. |

## 4. Rounding Rules

All rounding uses **ROUND_HALF_UP** (commercial rounding).

| Context | Rule |
|---------|------|
| Float → Money | `int(round(value * 10^scale))` |
| Decimal → Money | `int(value * 10^scale)` (no rounding, exact truncation) |
| Percentage calculations | Multiply first, then truncate toward zero |

## 5. Currency Rules

- Every `Money` instance has exactly one currency.
- Mixed-currency arithmetic raises `ValueError`.
- Accounts, transactions, and transfers must share the same currency within a household context.

## 6. Precision Policy

- **Store** as integer (no floating point in persistence).
- **Compute** with `Decimal` (Python `decimal.Decimal`).
- **Never** use `float` for intermediate financial calculations.
- Conversions `float → Decimal` or `Decimal → float` are only permitted at system boundaries (API responses, display).

## 7. Edge Cases

| Scenario | Behavior |
|----------|----------|
| Zero amount | `Money(0, "COP", 2)` is valid. |
| Max COP value | Limited by Python `int` (unbounded). |
| Discount 100% | `apply_discount(amount, Decimal("1"))` returns `Money(0, currency, scale)`. |
| Tax 0% | `apply_tax(amount, Decimal("0"))` returns original amount. |
| Negative tax | `apply_tax(amount, Decimal("-0.1"))` raises `ValueError`. |
| Discount > 100% | `apply_discount(amount, Decimal("1.1"))` raises `ValueError`. |

## 8. Display

```python
m.to_string()    # "85000.00" — for API JSON
m.to_display()   # "85,000.00 COP" — for UI
m.as_float       # 850.0 — for display only
m.as_decimal     # Decimal("850.00") — for calculations
```
