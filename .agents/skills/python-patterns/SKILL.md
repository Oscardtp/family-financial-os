---
name: python-patterns
description: Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications. Use when writing or reviewing Python code and idiomatic structure, typing, or PEP 8 is in question.
metadata:
  origin: ECC
---

# Python Development Patterns

Idiomatic Python patterns and best practices for building robust, efficient, and maintainable applications.

## Core Principles

### 1. Readability Counts
```python
# Good
def get_active_users(users: list[User]) -> list[User]:
    return [user for user in users if user.is_active]

# Bad
def get_active_users(u):
    return [x for x in u if x.a]
```

### 2. EAFP - Easier to Ask Forgiveness Than Permission
```python
# Good
def get_value(dictionary: dict, key: str, default_value: Any = None) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        return default_value
```

## Type Hints

```python
from typing import TypeVar

T = TypeVar('T')

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

## Error Handling

```python
class AppError(Exception): pass
class ValidationError(AppError): pass
class NotFoundError(AppError): pass
```

## Context Managers

```python
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{name} took {elapsed:.4f} seconds")
```

## Data Classes

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
```

## Anti-Patterns to Avoid

- Mutable default arguments: use `None` and create new list
- Checking type with `type()`: use `isinstance`
- Comparing to None with `==`: use `is`
- Bare except: use specific exception
- `from module import *`: use explicit imports
