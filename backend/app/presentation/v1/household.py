from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.presentation.deps import require_viewer, require_member, require_owner
from app.infrastructure.repositories.household_repository import SQLAlchemyHouseholdRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/household", tags=["Household"])


class InviteMember(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    role: str = Field("member", pattern="^(member|viewer)$")


class UpdateRole(BaseModel):
    role: str = Field(..., pattern="^(owner|member|viewer)$")


@router.get("", summary="Get household info", description="Returns household details and all members")
async def get_household(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    household_id = current_user["household_id"]
    if not household_id:
        raise HTTPException(status_code=404, detail="No encontramos tu hogar")

    repo = SQLAlchemyHouseholdRepository(db)
    household = await repo.get_by_id(household_id)
    if not household:
        raise HTTPException(status_code=404, detail="No encontramos este hogar")

    user_repo = SQLAlchemyUserRepository(db)
    members = await user_repo.get_all_by_household(household_id)

    return {
        "id": household["id"],
        "name": household["name"],
        "members": [
            {"id": m["id"], "email": m["email"], "name": m["name"], "role": m["role"]}
            for m in members
        ],
    }


@router.post("/invite", status_code=201, summary="Invite member", description="Invite a user to join the household by email")
async def invite_member(
    data: InviteMember,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    if current_user.get("role") not in ("owner",):
        raise HTTPException(status_code=403, detail="Solo los dueños pueden invitar miembros")

    user_repo = SQLAlchemyUserRepository(db)
    target = await user_repo.get_by_email(data.email)
    if not target:
        raise HTTPException(status_code=404, detail="No encontramos a esta persona. Primero debe crear su cuenta.")

    if target["household_id"] == current_user["household_id"]:
        raise HTTPException(status_code=400, detail="Esta persona ya está en tu hogar")

    household_repo = SQLAlchemyHouseholdRepository(db)
    await household_repo.add_member(current_user["household_id"], target["id"], data.role)
    await db.commit()

    return {"message": f"{data.email} se unió como {data.role}"}


@router.put("/members/{user_id}/role", summary="Change member role", description="Update a member's role (owner, member, viewer)")
async def update_member_role(
    user_id: str,
    data: UpdateRole,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    if current_user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Solo los dueños pueden cambiar roles")

    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="No puedes cambiar tu propio rol")

    user_repo = SQLAlchemyUserRepository(db)
    target = await user_repo.get_by_id(user_id)
    if not target or target["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos a este miembro")

    members = await user_repo.get_all_by_household(current_user["household_id"])
    owners = [m for m in members if m["role"] == "owner"]
    if len(owners) <= 1 and target["role"] == "owner" and data.role != "owner":
        raise HTTPException(status_code=400, detail="No puedes quitarle el rol de dueño al último dueño")

    await user_repo.update({**target, "role": data.role})
    await db.commit()
    return {"message": f"Rol actualizado a {data.role}"}


@router.delete("/members/{user_id}", summary="Remove member", description="Remove a member from the household")
async def remove_member(
    user_id: str,
    current_user: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    if current_user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Solo los dueños pueden eliminar miembros")

    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    user_repo = SQLAlchemyUserRepository(db)
    target = await user_repo.get_by_id(user_id)
    if not target or target["household_id"] != current_user["household_id"]:
        raise HTTPException(status_code=404, detail="No encontramos a este miembro")

    members = await user_repo.get_all_by_household(current_user["household_id"])
    owners = [m for m in members if m["role"] == "owner"]
    if len(owners) <= 1 and target["role"] == "owner":
        raise HTTPException(status_code=400, detail="No puedes eliminar al último dueño")

    await user_repo.update({**target, "household_id": None, "role": "member"})
    await db.commit()
    return {"message": "Miembro eliminado"}
