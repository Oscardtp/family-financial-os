# Project Context — Family Financial OS

## Overview

Family Financial OS is a personal and family financial management system designed to help households track income, expenses, budgets, debts, savings goals, and net worth. The project is currently undergoing migration from a Python/FastAPI + MySQL + vanilla JavaScript stack to a modern Next.js + TypeScript + Supabase + PostgreSQL + Prisma architecture.

## Target Users

- Individual users managing personal finances
- Families managing shared household finances
- Users who need detailed financial tracking and reporting

## Core Features

### Financial Management
- **Accounts**: Checking, savings, credit cards, cash, investments
- **Transactions**: Income, expenses, transfers with ledger entries
- **Categories**: Hierarchical income/expense categorization
- **Budgets**: Periodic budgets with progress tracking
- **Debts**: Debt tracking with payment schedules and amortization
- **Savings Goals**: Goal-based savings with progress tracking
- **Assets & Liabilities**: Net worth tracking
- **Recurring Transactions**: Automated recurring payments
- **Reports**: Cash flow, income vs expenses, category analysis, net worth

### Household Collaboration
- Multi-member households with role-based access
- Data isolation between households
- Shared financial visibility

### Audit & Compliance
- Immutable ledger entries
- Full transaction audit trail
- Balance calculation from ledger (not cached)

## Current State

### Existing Implementation
- **Backend**: Python/FastAPI with 98 REST endpoints
- **Frontend**: HTML5 + CSS3 + vanilla JavaScript SPA
- **Database**: MySQL 8.4+ with 19 tables
- **Architecture**: Domain-Driven Design with PHP-style layered structure

### Migration Target
- **Frontend**: Next.js 14+ with App Router
- **Backend**: Next.js API Routes (thin controllers)
- **Database**: PostgreSQL via Supabase
- **ORM**: Prisma
- **Validation**: Zod
- **Testing**: Vitest + Playwright

## Financial Rules

1. **Income**: Increases asset account balance, decreases liability account balance
2. **Expense**: Decreases asset account balance, increases liability account balance
3. **Transfer**: Source account -amount, destination account +amount (no net effect)
4. **Account Nature**:
   - Asset accounts: bank, cash, digital_wallet, savings, investment
   - Liability accounts: credit_card
5. **Money Precision**: All amounts stored as strings (exact decimal), never floats
6. **Ledger**: Immutable, append-only, balances calculated from entries
7. **No Overdraft**: Cannot spend more than available balance in asset accounts

## Non-Functional Requirements

- **Performance**: Dashboard loads in < 2 seconds
- **Security**: Row Level Security for all household data
- **Reliability**: Financial calculations must be 100% accurate
- **Testability**: Financial Engine must have 100% test coverage
- **Maintainability**: Framework-agnostic Financial Engine

## Constraints

- No microservices architecture
- No LLM for financial calculations
- No floating-point arithmetic for money
- Financial Engine must remain framework-independent
- Prisma is the PostgreSQL access layer only
- Supabase is infrastructure only (auth, storage, edge functions)
