"""Script to load real financial data from Excel into SQLite."""

import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import pandas as pd
from app.infrastructure.sqlite import init_db, get_connection, SQLiteRepository
from app.domain.domain import (
    Money, Timestamp, Account, AccountType, Transaction,
    TransactionType, TransactionStatus, Budget, Debt, Goal,
    Asset, Liability, Member, Household, User, Category
)
from datetime import datetime, timedelta
import uuid

# Initialize database
init_db()
repo = SQLiteRepository()

# Create default household
household = Household(
    id="default-household",
    name="Familia Proyecto 2026",
    country="CO",
    currency="COP",
    timezone="America/Bogota",
)
repo.create_household(household)

# Create a default user
user = User(
    id="default-user",
    name="Usuario",
    email="user@example.com",
    password_hash="hashed",
    household_id=household.id,
)
# User table doesn't exist yet in our schema, skip for now

print("Household created:", household.id)

# Create accounts
accounts = {
    "Efectivo": Account(id="acc-cash", name="Efectivo", account_type=AccountType.CASH, currency="COP", balance=Money(0, "COP", 2), household_id=household.id, initial_balance=Money(0, "COP", 2)),
    "Nequi": Account(id="acc-nequi", name="Nequi", account_type=AccountType.DIGITAL_WALLET, currency="COP", balance=Money(0, "COP", 2), household_id=household.id, initial_balance=Money(0, "COP", 2)),
    "Bancolombia": Account(id="acc-bancolombia", name="Bancolombia Ahorros", account_type=AccountType.BANK, currency="COP", balance=Money(0, "COP", 2), household_id=household.id, initial_balance=Money(0, "COP", 2)),
    "TC Visa": Account(id="acc-tc-visa", name="TC Visa", account_type=AccountType.CREDIT_CARD, currency="COP", balance=Money(0, "COP", 2), household_id=household.id, initial_balance=Money(0, "COP", 2)),
}

for acc in accounts.values():
    repo.create_account(acc)
    print(f"Account created: {acc.name} ({acc.id})")

# Read Excel file
file_path = r'DEUDAS PROYECCION 2026.xlsx'
xl = pd.ExcelFile(file_path)

# Process CREDITOS CONTROL sheet
print("\n--- Processing CREDITOS CONTROL ---")
df_credits = pd.read_excel(file_path, sheet_name='CREDITOS CONTROL')
print(df_credits.to_string())

# Create debts from real data
debts_data = [
    {"name": "Credito", "principal": 240000, "monthly_payment": 0, "creditor": "Desconocido", "status": "active"},
    {"name": "Maryi", "principal": 2000000, "monthly_payment": 100000, "creditor": "Desconocido", "status": "active"},
    {"name": "Brilla", "principal": 4200000, "monthly_payment": 0, "creditor": "Brilla", "status": "active"},
    {"name": "Tio Jose", "principal": 1000000, "monthly_payment": 0, "creditor": "Tio Jose", "status": "active"},
    {"name": "Yuleidys", "principal": 500000, "monthly_payment": 125000, "creditor": "Yuleidys", "status": "active"},
    {"name": "Rayo", "principal": 540000, "monthly_payment": 270000, "creditor": "Rayo", "status": "active"},
    {"name": "Rapicredit", "principal": 355000, "monthly_payment": 130000, "creditor": "Rapicredit", "status": "active"},
    {"name": "Davivienda", "principal": 38862000, "monthly_payment": 762000, "creditor": "Davivienda", "status": "active"},
    {"name": "ICETEX", "principal": 5000000, "monthly_payment": 229000, "creditor": "ICETEX", "status": "active"},
    {"name": "Siomara 1 Prestamo", "principal": 930000, "monthly_payment": 0, "creditor": "Siomara", "status": "active"},
    {"name": "Jeni Prestamo", "principal": 3000000, "monthly_payment": 0, "creditor": "Jeni", "status": "active"},
]

for debt_data in debts_data:
    debt = Debt(
        id=str(uuid.uuid4()),
        name=debt_data["name"],
        principal=Money(debt_data["principal"], "COP", 2),
        interest_rate=Decimal("0.00"),
        monthly_payment=Money(debt_data["monthly_payment"], "COP", 2),
        currency="COP",
        due_date=Timestamp(datetime(2026, 12, 31)),
        household_id=household.id,
        creditor=debt_data["creditor"],
        status=debt_data["status"],
    )
    repo.create_debt(debt)
    print(f"Debt created: {debt.name} - Balance: {debt.balance.to_string()}")

# Process PROYECCION PAGOS sheet
print("\n--- Processing PROYECCION PAGOS ---")
df_pagos = pd.read_excel(file_path, sheet_name='PROYECCION PAGOS')
print(df_pagos.head(20).to_string())

# Create categories based on payment types
categories = {
    "Servicios": Category(id="cat-servicios", name="Servicios", type="expense", household_id=household.id, icon="bolt", color="#9333EA"),
    "Internet": Category(id="cat-internet", name="Internet", type="expense", household_id=household.id, parent_id="cat-servicios", icon="wifi", color="#9333EA"),
    "Telefonia": Category(id="cat-telefonia", name="Telefonía", type="expense", household_id=household.id, parent_id="cat-servicios", icon="phone", color="#9333EA"),
    "Deudas": Category(id="cat-deudas", name="Deudas", type="expense", household_id=household.id, icon="credit-card", color="#DC2626"),
    "ICETEX": Category(id="cat-icetex", name="ICETEX", type="expense", household_id=household.id, parent_id="cat-deudas", icon="graduation-cap", color="#DC2626"),
    "Davivienda": Category(id="cat-davivienda", name="Davivienda", type="expense", household_id=household.id, parent_id="cat-deudas", icon="bank", color="#DC2626"),
    "Otros Prestamos": Category(id="cat-otros-prestamos", name="Otros Préstamos", type="expense", household_id=household.id, parent_id="cat-deudas", icon="handshake", color="#DC2626"),
    "Alimentacion": Category(id="cat-alimentacion", name="Alimentación", type="expense", household_id=household.id, icon="utensils", color="#16A34A"),
    "Mercado": Category(id="cat-mercado", name="Mercado", type="expense", household_id=household.id, parent_id="cat-alimentacion", icon="shopping-cart", color="#16A34A"),
    "Transporte": Category(id="cat-transporte", name="Transporte", type="expense", household_id=household.id, icon="car", color="#2563EB"),
    "Combustible": Category(id="cat-combustible", name="Combustible", type="expense", household_id=household.id, parent_id="cat-transporte", icon="gas-pump", color="#2563EB"),
    "Entretenimiento": Category(id="cat-entretenimiento", name="Entretenimiento", type="expense", household_id=household.id, icon="tv", color="#9333EA"),
    "Brilla": Category(id="cat-brilla", name="Brilla", type="expense", household_id=household.id, parent_id="cat-entretenimiento", icon="tv", color="#9333EA"),
    "Netflix": Category(id="cat-netflix", name="Netflix", type="expense", household_id=household.id, parent_id="cat-entretenimiento", icon="tv", color="#9333EA"),
    "Tigo": Category(id="cat-tigo", name="Tigo", type="expense", household_id=household.id, icon="phone", color="#9333EA"),
    "Claro": Category(id="cat-claro", name="Claro", type="expense", household_id=household.id, icon="phone", color="#9333EA"),
    "Celu Cuotas": Category(id="cat-celu-cuotas", name="Celulares Cuotas", type="expense", household_id=household.id, icon="smartphone", color="#9333EA"),
    "Recordar": Category(id="cat-recordar", name="Recordar", type="expense", household_id=household.id, icon="heart", color="#DC2626"),
    "Arriendo": Category(id="cat-arriendo", name="Arriendo", type="expense", household_id=household.id, icon="home", color="#2563EB"),
    "Tarjeta Papi": Category(id="cat-tarjeta-papi", name="Tarjeta Papi", type="expense", household_id=household.id, icon="credit-card", color="#DC2626"),
    "Yuleidys": Category(id="cat-yuleidys", name="Yuleidys", type="expense", household_id=household.id, icon="user", color="#2563EB"),
    "Sara": Category(id="cat-sara", name="Sara", type="expense", household_id=household.id, icon="user", color="#2563EB"),
    "Otros Gastos": Category(id="cat-otros-gastos", name="Otros Gastos", type="expense", household_id=household.id, icon="more-horizontal", color="#6B7280"),
    "Ingresos": Category(id="cat-ingresos", name="Ingresos", type="income", household_id=household.id, icon="briefcase", color="#059669"),
    "Salario": Category(id="cat-salario", name="Salario", type="income", household_id=household.id, parent_id="cat-ingresos", icon="briefcase", color="#059669"),
    "Freelance": Category(id="cat-freelance", name="Freelance", type="income", household_id=household.id, parent_id="cat-ingresos", icon="laptop", color="#059669"),
}

for cat in categories.values():
    repo.create_category(cat)
    print(f"Category created: {cat.name}")

print("\nReal data loaded successfully!")
print("\nNext steps:")
print("1. Run the backend: python backend/app/main.py")
print("2. Access API docs: http://localhost:8000/docs")
print("3. Use the frontend to interact with real data")
