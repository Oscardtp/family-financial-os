"""
Seed script to add admin@familia.com user with debts from Excel file.
Run: python -m seed_deudas
"""
import asyncio
import sys
import os
from datetime import date, datetime

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.database import async_session
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.household_repository import SQLAlchemyHouseholdRepository
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.infrastructure.repositories.debt_repository import SQLAlchemyDebtRepository
from app.presentation.deps import hash_password


async def seed():
    async with async_session() as db:
        # 1. Check if user already exists
        user_repo = SQLAlchemyUserRepository(db)
        existing = await user_repo.get_by_email("admin@familia.com")
        if existing:
            print(f"User admin@familia.com already exists with id: {existing['id']}")
            user = existing
            household_id = user["household_id"]
            if not household_id:
                print("User exists but has no household. Creating one...")
                household_repo = SQLAlchemyHouseholdRepository(db)
                household = await household_repo.create({"name": "Admin Familia's Household"})
                await household_repo.add_member(household["id"], user["id"], "owner")
                user = await user_repo.update({**user, "household_id": household["id"]})
                household_id = household["id"]
                print(f"Created household: {household_id}")
        else:
            # Create user
            user = await user_repo.create({
                "email": "admin@familia.com",
                "name": "Admin Familia",
                "password_hash": hash_password("admin123"),
                "role": "owner",
            })
            print(f"Created user: {user['id']}")

            # Create household
            household_repo = SQLAlchemyHouseholdRepository(db)
            household = await household_repo.create({"name": "Admin Familia's Household"})
            await household_repo.add_member(household["id"], user["id"], "owner")

            # Create default categories
            cat_repo = SQLAlchemyCategoryRepository(db)
            default_categories = [
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
            for cat in default_categories:
                await cat_repo.create({**cat, "household_id": household["id"]})

            # Update user with household_id
            user = await user_repo.update({**user, "household_id": household["id"]})
            household_id = household["id"]
            print(f"Created household: {household_id}")

        # 2. Add debts from Excel
        debt_repo = SQLAlchemyDebtRepository(db)

        # Check if debts already exist
        existing_debts = await debt_repo.get_all(household_id)
        if existing_debts:
            print(f"Household already has {len(existing_debts)} debts. Skipping creation.")
            print("Existing debts:")
            for d in existing_debts:
                print(f"  - {d['name']}: ${d['current_balance']:,.0f}")
        else:
            # Debts from CREDITOS CONTROL sheet
            debts = [
                {
                    "name": "Yuleidys",
                    "creditor": "Yuleidys",
                    "total_amount": 500000,
                    "current_balance": 0,  # Paid off (control shows 500k - 500k = 0)
                    "interest_rate": 0,
                    "minimum_payment": 125000,
                    "due_day": 30,
                    "start_date": date(2026, 1, 30),
                    "end_date": date(2026, 7, 30),
                    "status": "active",
                },
                {
                    "name": "Credito",
                    "creditor": "Credito",
                    "total_amount": 240000,
                    "current_balance": 240000,
                    "interest_rate": 0,
                    "minimum_payment": 0,
                    "due_day": 30,
                    "start_date": date(2026, 1, 30),
                    "end_date": date(2026, 8, 30),
                    "status": "active",
                },
                {
                    "name": "Rayo",
                    "creditor": "Rayo",
                    "total_amount": 540000,
                    "current_balance": 270000,  # 540k - 270k paid
                    "interest_rate": 0,
                    "minimum_payment": 270000,
                    "due_day": 30,
                    "start_date": date(2026, 1, 30),
                    "end_date": date(2026, 8, 30),
                    "status": "active",
                },
                {
                    "name": "Rapicredit",
                    "creditor": "Rapicredit",
                    "total_amount": 355000,
                    "current_balance": 225000,  # 355k - 130k paid
                    "interest_rate": 0,
                    "minimum_payment": 130000,
                    "due_day": 15,
                    "start_date": date(2026, 1, 15),
                    "end_date": date(2026, 9, 15),
                    "status": "active",
                },
                {
                    "name": "Tio Jose",
                    "creditor": "Tio Jose",
                    "total_amount": 1000000,
                    "current_balance": 1000000,
                    "interest_rate": 0,
                    "minimum_payment": 0,
                    "due_day": 30,
                    "start_date": date(2026, 1, 30),
                    "end_date": date(2026, 10, 30),
                    "status": "active",
                },
                {
                    "name": "Maryi",
                    "creditor": "Maryi",
                    "total_amount": 2000000,
                    "current_balance": 1800000,  # 2M - 200k paid
                    "interest_rate": 0,
                    "minimum_payment": 0,
                    "due_day": 30,
                    "start_date": date(2026, 1, 30),
                    "end_date": date(2026, 11, 30),
                    "status": "active",
                },
                {
                    "name": "Brilla",
                    "creditor": "Brilla",
                    "total_amount": 4200000,  # 2.2M + 2M
                    "current_balance": 4200000,
                    "interest_rate": 0,
                    "minimum_payment": 300000,  # 200k + 100k
                    "due_day": 30,
                    "start_date": date(2026, 7, 30),
                    "end_date": date(2027, 1, 30),
                    "status": "active",
                },
                {
                    "name": "ICETEX",
                    "creditor": "ICETEX",
                    "total_amount": 5000000,
                    "current_balance": 5000000,
                    "interest_rate": 0,
                    "minimum_payment": 229000,
                    "due_day": 30,
                    "start_date": date(2026, 1, 30),
                    "end_date": date(2027, 1, 30),
                    "status": "active",
                },
                {
                    "name": "Siomara 1 Prestamo",
                    "creditor": "Siomara",
                    "total_amount": 1330000,  # 800k + 130k + 400k
                    "current_balance": 1330000,
                    "interest_rate": 0,
                    "minimum_payment": 0,
                    "due_day": 15,
                    "start_date": date(2026, 1, 15),
                    "end_date": date(2027, 2, 15),
                    "status": "active",
                },
                {
                    "name": "Jeni Prestamo",
                    "creditor": "Jeni",
                    "total_amount": 3000000,
                    "current_balance": 3000000,
                    "interest_rate": 0,
                    "minimum_payment": 0,
                    "due_day": 28,
                    "start_date": date(2026, 1, 28),
                    "end_date": date(2027, 2, 28),
                    "status": "active",
                },
                {
                    "name": "Andres Dian",
                    "creditor": "Andres",
                    "total_amount": 2297000,
                    "current_balance": 2297000,
                    "interest_rate": 0,
                    "minimum_payment": 0,
                    "due_day": 1,
                    "start_date": None,
                    "end_date": None,
                    "status": "active",
                },
                {
                    "name": "Davivienda",
                    "creditor": "Davivienda",
                    "total_amount": 38862000,
                    "current_balance": 38862000,
                    "interest_rate": 0,
                    "minimum_payment": 762000,
                    "due_day": 1,
                    "start_date": date(2025, 10, 1),
                    "end_date": date(2027, 12, 30),
                    "status": "active",
                },
            ]

            for debt in debts:
                created = await debt_repo.create({**debt, "household_id": household_id})
                print(f"Created debt: {created['name']} - ${created['current_balance']:,.0f}")

            print(f"\nTotal debts created: {len(debts)}")
            total_balance = await debt_repo.get_total_balance(household_id)
            print(f"Total balance: ${total_balance:,.0f}")

        await db.commit()
        print("\nDone! User admin@familia.com with password 'admin123' is ready.")
        print(f"Household ID: {household_id}")


if __name__ == "__main__":
    asyncio.run(seed())
