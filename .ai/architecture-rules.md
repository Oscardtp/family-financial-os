# Architecture Rules — Family Financial OS

## Layered Architecture

The project follows a strict layered architecture where dependencies flow inward only.

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js (Presentation)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Infrastructure / Prisma Layer                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Supabase (Infrastructure)                │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Next.js (Presentation)
- Server Components for data fetching
- Client Components for interactivity
- Thin API Route handlers
- No business logic

### Application Layer
- Use cases / Services orchestrate workflows
- DTOs and mappers for type conversion
- Input validation (Zod)
- Transaction management

### Domain Layer
- Entities with behavior (not anemic)
- Value Objects (Money, Currency)
- Domain Services for complex logic
- Repository interfaces (ports)
- Business rules
- **ZERO external framework dependencies**

### Financial Engine (Framework-Agnostic)
- Pure functions for all calculations
- No I/O, no side effects
- Deterministic, fully testable
- Uses Decimal.js for precision
- No imports from any framework

### Infrastructure / Prisma Layer
- Repository implementations (adapters)
- Prisma Client configuration
- External service clients

### PostgreSQL
- Data persistence via Prisma
- RLS policies for security
- Constraints and triggers

### Supabase (Infrastructure)
- Authentication
- Storage (receipts, documents)
- Edge Functions (if needed)

## Dependency Rules

1. Inner layers must never depend on outer layers
2. Domain defines interfaces, Infrastructure implements them
3. Application depends only on Domain interfaces
4. Next.js depends on Application and Infrastructure
5. Financial Engine has zero external dependencies

## Financial Engine Isolation Rules

The Financial Engine (`domain/financial-engine/`) must never import:
- `@prisma/client`
- `@supabase/supabase-js`
- `next/*`
- Any external framework or library (except standard library + Decimal.js)

Allowed imports:
- Standard TypeScript/JavaScript
- `decimal.js` or `big.js`
- Internal domain types only

## Data Flow Rules

1. All financial operations flow through the Application layer
2. Domain entities contain behavior, not just data
3. Repository interfaces defined in Domain, implemented in Infrastructure
4. Prisma models are infrastructure concerns, never exposed to Domain
5. Supabase is never accessed from Domain or Financial Engine

## Household Isolation Rules

1. Every financial table has `household_id` column
2. All queries filter by `household_id`
3. RLS enforces household-level access
4. No cross-household data access permitted
5. User membership verified before operations

## Money Handling Rules

1. All amounts stored as strings in database
2. All calculations use Decimal.js
3. No JavaScript `number` for financial values
4. Currency always explicit (ISO 4217)
5. Validation at every boundary

## Test Strategy

| Layer | Test Type | Tool |
|-------|-----------|------|
| Financial Engine | Unit | Vitest |
| Domain | Unit | Vitest |
| Application | Integration | Vitest + test DB |
| Infrastructure | Integration | Vitest + test DB |
| Next.js | E2E | Playwright |

## Error Handling Rules

1. Domain exceptions defined in `domain/errors/`
2. Infrastructure maps database errors to domain exceptions
3. Application layer translates domain exceptions to HTTP responses
4. Never expose internal details in API error responses
5. Log errors server-side only
