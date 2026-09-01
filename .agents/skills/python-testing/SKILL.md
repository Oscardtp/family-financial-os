---
name: python-testing
description: Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements. Use when writing pytest tests — fixtures, mocks, parametrization, or coverage.
metadata:
  origin: ECC
---

# Python Testing Patterns

Comprehensive testing strategies for Python applications using pytest, TDD, and best practices.

## TDD Cycle

1. **RED**: Write a failing test
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Improve code while keeping tests green

## pytest Fixtures

```python
@pytest.fixture
def database():
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

@pytest.fixture(scope="module")
def module_db():
    db = Database(":memory:")
    yield db
    db.close()

@pytest.fixture(autouse=True)
def reset_config():
    Config.reset()
    yield
    Config.cleanup()
```

## Parametrization

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

## Mocking

```python
from unittest.mock import patch, Mock

@patch("mypackage.external_api_call")
def test_with_mock(api_call_mock):
    api_call_mock.return_value = {"status": "success"}
    result = my_function()
    api_call_mock.assert_called_once()
```

## Async Testing

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_add(2, 3)
    assert result == 5
```

## Testing Exceptions

```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

## pytest Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-markers", "--cov=mypackage", "--cov-report=term-missing"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

## Best Practices

- Follow TDD (red-green-refactor)
- Test one thing per test
- Use descriptive names: `test_user_login_with_invalid_credentials_fails`
- Mock external dependencies
- Test edge cases: empty inputs, None values, boundary conditions
- Aim for 80%+ coverage on critical paths
