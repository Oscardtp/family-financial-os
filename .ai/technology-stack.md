# Technology Stack

## Verificado en este entorno (Node v24.18, Windows 11 PS 5.1)

| Dependencia | Versión | Estado | Nota |
|---|---|---|---|
| next | 16.3.0 | instalado | App Router (único paradigma) |
| react / react-dom | 19.2.8 | instalado | peer de Next 16 |
| typescript | 5.9.3 | instalado | `npx tsc --noEmit` → 0 errores |
| @prisma/client | 7.9.1 | instalado | cliente ORM v7 (rust-free) |
| prisma (dev) | 7.9.1 | instalado | CLI v7 |
| @prisma/adapter-pg | 7.x | instalado | driver adapter directo (Postgres) |
| pg | 8.x | instalado | peer de @prisma/adapter-pg |
| dotenv | 16.x | instalado (dev) | carga `.env` en `prisma.config.ts` |
| zod | 4.4.3 | instalado | validación DTOs |
| vitest (dev) | 4.1.10 | instalado | `npm test` → 2/2 PASS |
| eslint 9 + eslint-config-next 16 + prettier | 3.9.6 | instalados | `npm run lint` → 0 problemas |
| @supabase/supabase-js | — | **pendiente** | auth, fase web |
| dinero.js | 2.0.2 | **pendiente** | motor Money, fase engine |

## Estado de la DB local — PROVISIONADA Y VALIDADA ✅

- **PostgreSQL 17.10 portable** (EDB no-installer), **sin Docker, sin cuenta**.
- Binarias: `C:\Users\HP\AppData\Local\Programs\pg17\pgsql\bin` (pg_ctl, initdb, postgres, psql).
- Data dir: `C:\Users\HP\AppData\Local\pgdata-ffos` (initdb con `-U postgres -A trust`).
- Puerto **5432**, auth `trust` (dev local). Base `ffos`.
- `DATABASE_URL="postgresql://postgres@127.0.0.1:5432/ffos?schema=public"` (en `.env`, gitignorado).
- `prisma migrate dev --name init` aplicada → tablas: Account, Transaction, LedgerLine, Budget,
  Goal, NetWorthSnapshot (+ enums + FKs + índices). `prisma validate` 🚀.
- Smoke test PASS: `Transaction.create` (sin id) genera UUID v7 y persiste contra Postgres local.
- ⚠️ El sandbox mata `postgres.exe` al cerrar la sesión del agente → **arrancar pg por sesión**
  (`pg_ctl -D "...\pgdata-ffos" -w start` o `postgres.exe -D <data>` vía `Start-Process`).

## Scripts npm (package.json)

`dev` | `build` | `start` | `lint` | **`test`** (`vitest run`) | `test:watch` |
`prisma:generate` | `prisma:migrate:dev` | `prisma:studio`.

## Prisma 7 — patrones (verificados con firecrawl-developer-index)

### 1. Conexión fuera del schema (breaking change de v7)
`datasource.url` se eliminó en Prisma 7 — la conexión vive en `prisma.config.ts` (root), no en schema.prisma.

`prisma.config.ts`:
```ts
import "dotenv/config";
import { defineConfig, env } from "prisma/config";
export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: { path: "prisma/migrations" },
  datasource: { url: env("DATABASE_URL") },
});
```
`schema.prisma`:
```prisma
datasource db { provider = "postgresql" }   // sin url
generator client { provider = "prisma-client-js" }
```
> `env("DATABASE_URL")` lanza si falta. En CI que solo hace `prisma generate`, usar `process.env.DATABASE_URL!`.

### 2. Cliente runtime con driver adapter (Prisma 7, rust-free)
```ts
import { PrismaClient } from "@prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL! });
new PrismaClient({ adapter });                          // runtime directo a Postgres
```

### 3. Singleton + HMR (sin fuges de conexiones)
```ts
// src/infra/database/prisma.ts
import { PrismaClient } from "@prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
declare global { var prisma: PrismaClient | undefined }
function createClient() {
  return new PrismaClient({ adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL! }) });
}
const client = global.prisma ?? createClient();
if (process.env.NODE_ENV !== "production") global.prisma = client;
export default client;
```
Fuente: docs.prisma.io + prisma/prisma#17566 (evita múltiples instancias en HMR).

### 4. UUIDs v7 — `@default(uuid(7))`
Prisma 7 PSL soporta `uuid(7)`: el UUID v7 se genera **cliente-side** (no necesita `DEFAULT` DB; se verificó
que `column_default` queda vacío y `create` sin id devuelve un UUID v7). Satisface R6 de architecture-rules.

## Supabase (deferred — auth fuera de scope)
No instalado. Pattern server-side verificado (docs oficiales): `createServerClient` de `@supabase/ssr` +
cookies httpOnly + `getUser()` en route handlers; `middleware.ts` protege rutas. Se añade en la fase de auth.
