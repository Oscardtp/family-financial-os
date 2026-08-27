from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_member
from app.presentation.schemas.schemas import (
    CategoryAccountPreferenceCreate,
    CategoryAccountPreferenceResponse,
)
from app.infrastructure.repositories.category_account_preference_repository import (
    SQLAlchemyCategoryAccountPreferenceRepository,
)

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get(
    "",
    response_model=list[CategoryAccountPreferenceResponse],
    summary="List category account preferences",
    description="Returns all saved category-to-account preferences for the household",
)
async def list_preferences(
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryAccountPreferenceRepository(db)
    return await repo.get_all(current_user["household_id"])


@router.post(
    "",
    response_model=CategoryAccountPreferenceResponse,
    status_code=201,
    summary="Create or update category account preference",
    description="Save or update the default account for a category (used for quick-add source memory)",
)
async def create_or_update_preference(
    data: CategoryAccountPreferenceCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryAccountPreferenceRepository(db)
    result = await repo.create_or_update({
        "household_id": current_user["household_id"],
        "category_id": str(data.category_id),
        "account_id": str(data.account_id),
    })
    await db.commit()
    return result


@router.delete(
    "/{category_id}",
    status_code=204,
    summary="Delete category account preference",
    description="Remove the default account for a category",
)
async def delete_preference(
    category_id: str,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyCategoryAccountPreferenceRepository(db)
    await repo.delete(current_user["household_id"], category_id)
    await db.commit()
