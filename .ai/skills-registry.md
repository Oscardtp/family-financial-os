# Skills Registry — Family Financial OS

This registry documents all skills bootstrapped for the Family Financial OS project, their versions, sources, and installation paths.

## Installed Skills

| # | Skill Name | Source | Source Type | Version | Path |
|---|-----------|--------|-------------|---------|------|
| 1 | supabase | supabase/supabase | github | 0.1.2 | `.kilo/skills/supabase/SKILL.md` |
| 2 | supabase-postgres-best-practices | supabase/supabase | github | 1.1.1 | `.kilo/skills/supabase-postgres-best-practices/SKILL.md` |
| 3 | prisma-database-setup | prisma/prisma | github | 7.6.0 | `.kilo/skills/prisma-database-setup/SKILL.md` |
| 4 | prisma-client-api | prisma/prisma | github | 7.9.1 | `.kilo/skills/prisma-client-api/SKILL.md` |
| 5 | architecture-patterns | secondsky/claude-skills | github | 1.0.0 | `.kilo/skills/architecture-patterns/SKILL.md` |
| 6 | vitest-testing | vitest-dev/vitest | github | latest | `.kilo/skills/vitest-testing/SKILL.md` |
| 7 | playwright | microsoft/playwright | github | latest | `.kilo/skills/playwright/SKILL.md` |
| 8 | e2e-testing | custom | internal | 1.0.0 | `.kilo/skills/e2e-testing/SKILL.md` |
| 9 | application-security | custom | internal | 1.0.0 | `.kilo/skills/application-security/SKILL.md` |
| 10 | postgresql-table-design | custom | internal | 1.0.0 | `.kilo/skills/postgresql-table-design/SKILL.md` |
| 11 | conventional-commits | conventional-commits | spec | 1.0.0 | `.kilo/skills/conventional-commits/SKILL.md` |
| 12 | zod | colinhacks/zod | github | latest | `.kilo/skills/zod/SKILL.md` |
| 13 | nextjs-app-router-patterns | vercel/next.js | github | latest | `.kilo/skills/nextjs-app-router-patterns/SKILL.md` |

## Coverage by Project Layer

| Layer | Skills | Coverage |
|-------|--------|----------|
| Next.js | nextjs-app-router-patterns | Pages, routing, API routes, Server/Client Components |
| Application | zod, architecture-patterns | Validation, use cases, DTOs, service orchestration |
| Domain | architecture-patterns | Entities, value objects, repository interfaces |
| Financial Engine | architecture-patterns, vitest-testing | Pure functions, Decimal.js, deterministic calculations |
| Prisma | prisma-database-setup, prisma-client-api | Schema, migrations, queries, transactions |
| PostgreSQL | supabase-postgres-best-practices, postgresql-table-design | RLS, indexes, constraints, table design |
| Supabase | supabase, supabase-postgres-best-practices | Auth, storage, infrastructure, best practices |
| Testing | vitest-testing, playwright, e2e-testing | Unit, integration, E2E, cross-browser |
| Security | application-security | Auth, authorization, input validation, injection prevention |
| Process | conventional-commits | Commit standards, changelog, versioning |

## Selection Criteria Applied

- **Official**: Skills from official repositories (supabase, prisma, zod, next.js, playwright)
- **Actively Maintained**: All selected skills have active maintenance
- **Well-Documented**: Comprehensive documentation available
- **Compatible**: No conflicts between skills
- **Non-Redundant**: Each skill covers distinct concerns
- **Project-Relevant**: Directly applicable to the target stack

## Removed Skills

| Skill | Source | Reason |
|-------|--------|--------|
| php-pro | davila7/claude-code-templates | Project migrated from PHP/FastAPI |
| xlsx | HKUDS/DeepTutor | Excel handling not a core development concern |

## Update Policy

When updating skills:
1. Check `skills-lock.json` for current versions
2. Update `SKILL.md` content if patterns change
3. Document breaking changes in `conventional-commits`
4. Run tests to verify compatibility
