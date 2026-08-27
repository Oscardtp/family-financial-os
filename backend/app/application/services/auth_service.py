from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.household_repository import SQLAlchemyHouseholdRepository
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.presentation.deps import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.presentation.schemas.schemas import TokenResponse


DEFAULT_CATEGORIES = [
    {"name": "Salario", "type": "income", "icon": "💰", "color": "#22c55e"},
    {"name": "Freelance", "type": "income", "icon": "💻", "color": "#3b82f6"},
    {"name": "Inversiones", "type": "income", "icon": "📈", "color": "#8b5cf6"},
    {"name": "Comida", "type": "expense", "icon": "🍎", "color": "#ef4444"},
    {"name": "Casa", "type": "expense", "icon": "🏠", "color": "#f97316"},
    {"name": "Transporte", "type": "expense", "icon": "🚗", "color": "#eab308"},
    {"name": "Servicios", "type": "expense", "icon": "💡", "color": "#84cc16"},
    {"name": "Salud", "type": "expense", "icon": "💊", "color": "#22c55e"},
    {"name": "Educacion", "type": "expense", "icon": "🎓", "color": "#14b8a6"},
    {"name": "Gustos", "type": "expense", "icon": "🎮", "color": "#06b6d4"},
    {"name": "Compras", "type": "expense", "icon": "👕", "color": "#3b82f6"},
    {"name": "Deudas", "type": "expense", "icon": "💳", "color": "#8b5cf6"},
    {"name": "Familia", "type": "expense", "icon": "❤️", "color": "#ec4899"},
    {"name": "Otros", "type": "expense", "icon": "📦", "color": "#6b7280"},
]


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = SQLAlchemyUserRepository(db)
        self.household_repo = SQLAlchemyHouseholdRepository(db)
        self.category_repo = SQLAlchemyCategoryRepository(db)

    async def register(self, data) -> TokenResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Este correo ya está registrado")

        user = await self.user_repo.create({
            "email": data.email,
            "name": data.name,
            "password_hash": hash_password(data.password),
            "role": "owner",
        })

        if not user.get("household_id"):
            household = await self.household_repo.create({"name": f"{data.name}'s Household"})
            await self.household_repo.add_member(household["id"], user["id"], "owner")

            for cat in DEFAULT_CATEGORIES:
                await self.category_repo.create({**cat, "household_id": household["id"]})

            updated_user = await self.user_repo.update({**user, "household_id": household["id"]})
            if not updated_user.get("household_id"):
                raise HTTPException(status_code=500, detail="No pudimos completar tu registro. Intenta de nuevo.")

        access = create_access_token({"sub": str(user["id"])})
        refresh = create_refresh_token({"sub": str(user["id"])})
        return TokenResponse(access_token=access, refresh_token=refresh)

    async def login(self, data) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

        access = create_access_token({"sub": str(user["id"])})
        refresh = create_refresh_token({"sub": str(user["id"])})
        return TokenResponse(access_token=access, refresh_token=refresh)

    async def refresh(self, token: str) -> TokenResponse:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Sesión no válida")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="No encontramos tu cuenta")

        access = create_access_token({"sub": str(user["id"])})
        refresh = create_refresh_token({"sub": str(user["id"])})
        return TokenResponse(access_token=access, refresh_token=refresh)
