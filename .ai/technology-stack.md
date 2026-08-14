# Technology Stack — Family Financial OS

## Target Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Framework | Next.js | 14+ | App Router, SSR, API Routes |
| Language | TypeScript | 5.x | Type safety across stack |
| Database | PostgreSQL | 16+ | Primary data store |
| ORM | Prisma | 5.x | Database access layer |
| Infrastructure | Supabase | Latest | Auth, storage, edge functions |
| Validation | Zod | 3.x | Runtime schema validation |
| Testing (Unit) | Vitest | 1.x | Fast unit/integration tests |
| Testing (E2E) | Playwright | 1.x | Browser automation tests |
| Decimal Math | Decimal.js | 10.x | Financial calculations |
| Linting | ESLint | 8.x | Code quality |
| Formatting | Prettier | 3.x | Code formatting |

## Why These Technologies

### Next.js + TypeScript
- Industry standard for React applications
- Built-in SSR, SSG, ISR for performance
- TypeScript ensures type safety across frontend and API
- Large ecosystem and community support

### PostgreSQL
- ACID compliance critical for financial data
- Advanced features: CTEs, window functions, JSON
- Row Level Security built-in
- Supabase integration

### Prisma
- Type-safe database access
- Excellent TypeScript integration
- Migration management
- Works with PostgreSQL and Supabase

### Supabase
- Open source Firebase alternative
- Built-in authentication
- PostgreSQL with RLS
- Storage and real-time features
- Easy local development

### Zod
- TypeScript-first validation
- Composable schemas
- Excellent TypeScript inference
- Works seamlessly with React Hook Form

### Vitest
- Fast, Vite-native testing
- Excellent TypeScript support
- Compatible with Jest API
- Built-in coverage

### Playwright
- Cross-browser testing
- Auto-waiting for elements
- Trace viewer for debugging
- Excellent CI/CD integration

### Decimal.js
- Arbitrary precision decimal arithmetic
- Prevents floating-point errors in financial calculations
- Well-maintained and performant

## Deprecated Technologies

| Technology | Reason for Replacement |
|------------|------------------------|
| Python/FastAPI | Migrating to Next.js full-stack |
| MySQL | Replaced by PostgreSQL for RLS and advanced features |
| PDO | Replaced by Prisma |
| Vanilla JS | Replaced by React + TypeScript |
| Custom CSS | Migrated to Tailwind CSS (planned) |

## Environment Requirements

- Node.js 18+
- PostgreSQL 16+ (or Supabase)
- npm or pnpm
- Git

## Package Structure

```
package.json (root)
├── Dependencies: next, react, react-dom, @prisma/client, @supabase/*, zod, decimal.js
├── DevDependencies: vitest, @vitest/coverage-v8, @playwright/test, typescript, eslint, prettier
```

## Configuration Files

- `tsconfig.json` - TypeScript configuration
- `vitest.config.ts` - Vitest configuration
- `playwright.config.ts` - Playwright configuration
- `next.config.js` - Next.js configuration
- `eslint.config.js` - ESLint flat config
- `prettier.config.js` - Prettier configuration
- `.env` - Environment variables
- `.env.example` - Environment variable template
- `prisma/schema.prisma` - Database schema
