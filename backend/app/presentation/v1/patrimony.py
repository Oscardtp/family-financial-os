from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.presentation.schemas.schemas import (
    AssetCreate, AssetUpdate, AssetResponse,
    LiabilityCreate, LiabilityUpdate, LiabilityResponse,
)
from app.infrastructure.repositories.asset_repository import SQLAlchemyAssetRepository
from app.infrastructure.repositories.liability_repository import SQLAlchemyLiabilityRepository

router = APIRouter(prefix="/patrimony", tags=["Patrimony"])


@router.get("/assets", response_model=list[AssetResponse], summary="List assets", description="Returns all registered assets")
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAssetRepository(db)
    return await repo.get_all(current_user["household_id"], skip, limit)


@router.post("/assets", response_model=AssetResponse, status_code=201, summary="Register asset", description="Add a new asset (property, vehicle, etc.)")
async def create_asset(
    data: AssetCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAssetRepository(db)
    result = await repo.create({
        "household_id": current_user["household_id"],
        **data.model_dump(),
    })
    await db.commit()
    return result


@router.put("/assets/{asset_id}", response_model=AssetResponse, summary="Update asset", description="Modify asset details")
async def update_asset(
    asset_id: str,
    data: AssetUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset or asset["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos este activo")

    update_data = data.model_dump(exclude_unset=True)
    if "value" in update_data:
        update_data["value"] = float(update_data["value"])

    result = await repo.update({**asset, **update_data})
    await db.commit()
    return result


@router.delete("/assets/{asset_id}", status_code=204, summary="Delete asset", description="Remove an asset record")
async def delete_asset(
    asset_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyAssetRepository(db)
    asset = await repo.get_by_id(asset_id)
    if not asset or asset["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos este activo")
    await repo.delete(asset_id)
    await db.commit()


@router.get("/liabilities", response_model=list[LiabilityResponse], summary="List liabilities", description="Returns all registered liabilities")
async def list_liabilities(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyLiabilityRepository(db)
    return await repo.get_all(current_user["household_id"], skip, limit)


@router.post("/liabilities", response_model=LiabilityResponse, status_code=201, summary="Register liability", description="Add a new liability (mortgage, loan, etc.)")
async def create_liability(
    data: LiabilityCreate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyLiabilityRepository(db)
    result = await repo.create({
        "household_id": current_user["household_id"],
        **data.model_dump(),
    })
    await db.commit()
    return result


@router.put("/liabilities/{liability_id}", response_model=LiabilityResponse, summary="Update liability", description="Modify liability details")
async def update_liability(
    liability_id: str,
    data: LiabilityUpdate,
    current_user: dict = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyLiabilityRepository(db)
    liability = await repo.get_by_id(liability_id)
    if not liability or liability["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos este pasivo")

    update_data = data.model_dump(exclude_unset=True)
    for key in ["current_balance", "interest_rate", "interest_rate_type", "monthly_payment"]:
        if key in update_data:
            update_data[key] = float(update_data[key])

    result = await repo.update({**liability, **update_data})
    await db.commit()
    return result


@router.delete("/liabilities/{liability_id}", status_code=204, summary="Delete liability", description="Remove a liability record")
async def delete_liability(
    liability_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyLiabilityRepository(db)
    liability = await repo.get_by_id(liability_id)
    if not liability or liability["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos este pasivo")
    await repo.delete(liability_id)
    await db.commit()
