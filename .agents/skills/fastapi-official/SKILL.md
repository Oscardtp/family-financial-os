---
name: fastapi-official
description: Official FastAPI best practices and conventions. Use when working with FastAPI APIs, Pydantic models, dependencies, streaming responses, and serving frontend apps. Keeps FastAPI code clean and up to date.
---

# FastAPI Official Skill

## Quick Reference

* Use `Annotated[..., Depends(...)]` for dependencies
* Use `app.frontend()` to serve built frontend assets
* Prefer return types over `response_model` when possible
* Use `def` for blocking code, `async` only for truly async operations
* Do not use `ORJSONResponse` or `UJSONResponse` (deprecated)

## Use `Annotated`

```python
from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(ge=1, description="The item ID")],
    q: Annotated[str | None, Query(max_length=50)] = None,
):
    return {"message": "Hello World"}
```

## Dependency Injection with Type Aliases

```python
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

@app.get("/items/")
async def read_item(current_user: CurrentUserDep):
    return {"message": "Hello World"}
```

## Router-Level Parameters

```python
router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_user)],
)
```

## Do Not Use Ellipsis

```python
class Item(BaseModel):
    name: str
    price: float = Field(gt=0)
```

## Serve Frontend Apps

```python
app.frontend("/", directory="dist")
```

## Async vs Sync

Use `def` by default (runs in threadpool). Use `async` only when certain the logic is async-compatible.

## Tooling

Use uv, Ruff, ty, Asyncer, SQLModel, HTTPX when applicable.
