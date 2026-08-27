from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.presentation.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse], summary="List categories", description="Returns all income and expense categories")
async def list_categories(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryRepository(db)
    return await repo.get_all(current_user["household_id"])


@router.post("", response_model=CategoryResponse, status_code=201, summary="Create category", description="Add a new transaction category")
async def create_category(
    data: CategoryCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryRepository(db)
    return await repo.create({
        "household_id": current_user["household_id"],
        **data.model_dump(),
    })


@router.put("/{category_id}", response_model=CategoryResponse, summary="Update category", description="Modify category name, icon, or color")
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryRepository(db)
    category = await repo.get_by_id(category_id)
    if not category or category["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos esta categoría")
    update_data = data.model_dump(exclude_unset=True)
    return await repo.update({**category, **update_data})


@router.delete("/{category_id}", status_code=204, summary="Delete category", description="Remove a transaction category")
async def delete_category(
    category_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryRepository(db)
    category = await repo.get_by_id(category_id)
    if not category or category["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos esta categoría")
    await repo.delete(category_id)
