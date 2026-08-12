# Current State (Bootstrap)

Estado tras la fase de integración de Agent Skills + DB local.

## Entorno
- OS: Windows 11 PowerShell 5.1 (skill `powershell-windows` activa). Node.js v24.18.0.
- PostgreSQL **17.10 portable local** en `127.0.0.1:5432` (trust), db `ffos`, **provisionada y funcionando**.
- `git` disponible (Git for Windows): `C:\Users\HP\AppData\Local\Programs\Git\cmd\git.exe`.

## Verificado ✅

| Check | Comando | Resultado |
|---|---|---|
| Scaffold Next 16 | `npx next --version` | 16.3.0 |
| Typecheck | `npx tsc --noEmit` | 0 errores |
| Lint | `npx eslint .` | 0 problemas |
| Prisma schema | `npx prisma validate` | válido 🚀 |
| Prisma client | `npx prisma generate` | Generado v7.9.1 |
| Migración | `npx prisma migrate dev --name init` | aplicada (7 tablas + enums + FKs) |
| Vitest suite | `npx vitest run` | **9/9 PASS** (DB smoke 2 + Money 7) |

## Stack instalado
Core (next 16.3, react 19, typescript 5.9, zod 4.4.3, eslint 9 + config-next, prettier); Data (prisma 7.9.1, @prisma/client 7.9.1, @prisma/adapter-pg, pg, dotenv); Engine (dinero.js v2 — `bigint` subpath); Test (vitest 4.1.10, vitest.config.mts); DevOps (prisma.config.ts).
Pendientes por instalar: `@supabase/supabase-js` + `@supabase/ssr` (auth).

## Arquitectura de capas creada (parcial)
```
src/
 ├─ infra/
 │    ├─ database/prisma.ts          # singleton PrismaClient v7 + PrismaPg adapter
 │    └─ __tests__/prisma.smoke.test.ts   # 2 tests (DB smoke + conexión + v7 id)
 └─ shared/
      └─ money/
           ├─ money.ts               # VO Money (bigint, Dinero.js v2 bigint subpath)
           └─ money.test.ts          # 7 tests (add/subtract/negate/cmp/mismatch/immutable)
prisma/
 ├─ schema.prisma                  # modelo User(id uuid v7) + Transaction(id uuid v7, FK)
 ├─ migrations/20260812025757_init/migration.sql
 └─ ... (más migraciones futuras)
prisma.config.ts                   # Prisma 7: datasource.url = env("DATABASE_URL")
vitest.config.mts                  # alias @ -> src (fileURLToPath, Windows-safe)
.ai/                               # memoria canónica del agente
docs/decisions/                    # ADRs 001-006
AGENTS.md                          # Project Rules añadido
```

## Estado de skills
- `powershell-windows` INSTALAR — activa.
- `firecrawl-developer-index` INSTALAR — activa + verificada (Prisma 7 breaking + PrismaPg + uuid(v7)).
- `firecrawl-search` INSTALAR — disponible.
- Catálogo: `.ai/skills-registry.md` (28 skills evaluadas).

## Pendientes (fases siguientes)
1. Auth: instalar `@supabase/supabase-js` + `@supabase/ssr`; wire `UserId` branded; `middleware.ts`.
2. Money ✅: Dinero.js v2 en `shared/money` (bigint) + 7 tests PASS (base del Financial Engine).
3. Engine de dominio: `transactions` (doble entrada), `accounts`, `budgets`, `goals`,
   `net-worth` + repositorios (interfaces Prisma) + tests puros.
4. API: route handlers (Next 16) validados con Zod → use-cases → repositorios.
5. Frontend Web + Mobile (futuro).
6. GitHub: push + CI (lint/typecheck/test en pipeline).

## Próximos pasos inmediatos
1. ✅ Bootstrap commit (24dfb3a).
2. ✅ Money (Dinero.js v2) + tests → base del Financial Engine. **PENDIENTE COMMIT**: incremento `Money` validado (ts/lint/9 tests verde) — esperando OK para commitear.
3. Next pick: (a) `transactions` engine doble-entrada + tests, o (b) Auth (Supabase).

(End of file)
